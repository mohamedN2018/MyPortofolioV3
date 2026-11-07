"""
Access control, audit logging, rate limiting, TOTP MFA and agent authentication.
"""
import base64
import functools
import hashlib
import hmac
import secrets
import struct
import time
from datetime import timedelta

from django.conf import settings
from django.core import signing
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from .models import AgentDevice, AuditEvent, HubSettings, OwnerMFA

ACCESS_TOKEN_TTL = 15 * 60      # seconds

MFA_SESSION_KEY = "hub_mfa_ok"


# ------------------------------------------------------------------ helpers
def client_ip(request):
    ip = request.META.get("HTTP_CF_CONNECTING_IP") or request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0]
    ip = (ip or request.META.get("REMOTE_ADDR") or "").strip()
    return ip or None


def audit(action, *, request=None, user=None, device=None, level="read", target=None, outcome="ok", **details):
    actor_type = "agent" if device else ("user" if (user or (request and getattr(request, "user", None) and request.user.is_authenticated)) else "system")
    if request is not None and user is None and getattr(request, "user", None) and request.user.is_authenticated:
        user = request.user
    target_type, target_id = "", ""
    if target is not None:
        target_type, target_id = target.__class__.__name__, str(target.pk)
    # Defence in depth: never persist anything that looks like a secret.
    clean = {k: ("[redacted]" if any(s in k.lower() for s in ("token", "secret", "password", "cookie", "authorization", "code")) else v)
             for k, v in details.items()}
    return AuditEvent.objects.create(
        actor_type=actor_type, actor_label=(device.name if device else (user.get_username() if user else "system")),
        user=user, device=device, action=action, level=level, target_type=target_type, target_id=target_id,
        outcome=outcome, ip=client_ip(request) if request else None, details=clean)


def rate_limited(key, limit, window):
    """Fixed-window counter stored in the DB (shared by every worker). True when the limit is exceeded."""
    from django.db import IntegrityError, transaction
    from django.db.models import F
    from .models import RateBucket
    bucket = f"{key}:{int(time.time() // window)}"[:160]
    updated = RateBucket.objects.filter(key=bucket).update(count=F("count") + 1)
    if not updated:
        try:
            with transaction.atomic():
                RateBucket.objects.create(key=bucket, count=1, expires_at=timezone.now() + timedelta(seconds=window))
        except IntegrityError:
            RateBucket.objects.filter(key=bucket).update(count=F("count") + 1)
        if secrets.randbelow(50) == 0:
            RateBucket.objects.filter(expires_at__lt=timezone.now()).delete()
    return RateBucket.objects.filter(key=bucket).values_list("count", flat=True).first() > limit


def limit_reached(key, limit, window):
    """Read-only check of a rate_limited() counter (used to count failures only)."""
    from .models import RateBucket
    bucket = f"{key}:{int(time.time() // window)}"[:160]
    return (RateBucket.objects.filter(key=bucket).values_list("count", flat=True).first() or 0) >= limit


# ------------------------------------------------------------------ owner access
def is_owner(user):
    return bool(user and user.is_authenticated and user.is_active and user.is_superuser)


def mfa_required_for(user):
    mfa = OwnerMFA.objects.filter(user=user, enabled=True).first()
    return mfa


def owner_required(view):
    """Every private page: logged-in superuser + (if enabled) a verified TOTP for this session."""
    @functools.wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('hub:login')}?next={request.path}")
        if not is_owner(request.user):
            audit("access_denied", request=request, outcome="denied", path=request.path)
            return HttpResponseForbidden("Forbidden")
        if mfa_required_for(request.user) and not request.session.get(MFA_SESSION_KEY):
            return redirect(f"{reverse('hub:mfa')}?next={request.path}")
        response = view(request, *args, **kwargs)
        response["X-Robots-Tag"] = "noindex, nofollow"
        response["Cache-Control"] = "private, no-store"
        response["Referrer-Policy"] = "same-origin"
        return response
    return wrapper


# ------------------------------------------------------------------ TOTP (RFC 6238, SHA1, 30s, 6 digits)
def new_totp_secret():
    return base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")


def _hotp(secret_b32, counter):
    key = base64.b32decode(secret_b32 + "=" * (-len(secret_b32) % 8))
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = (struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF) % 1_000_000
    return f"{code:06d}"


def totp_now(secret_b32, at=None):
    return _hotp(secret_b32, int((at or time.time()) // 30))


def verify_totp(mfa: OwnerMFA, code: str) -> bool:
    code = (code or "").strip().replace(" ", "")
    if not (len(code) == 6 and code.isdigit()):
        return False
    step = int(time.time() // 30)
    for candidate in (step - 1, step, step + 1):
        if candidate > mfa.last_used_step and hmac.compare_digest(_hotp(mfa.secret, candidate), code):
            mfa.last_used_step = candidate  # a code can never be replayed
            mfa.save(update_fields=["last_used_step"])
            return True
    return False


def totp_uri(secret, account):
    return f"otpauth://totp/Mohamed%20Nabil%20AI%20Hub:{account}?secret={secret}&issuer=Mohamed%20Nabil%20AI%20Hub"


# ------------------------------------------------------------------ agent authentication
_signer = signing.TimestampSigner(salt="hub.agent.access")


def parse_device_credential(credential):
    """mnpdev_<prefix>_<secret> -> (device, secret) or (None, None)."""
    try:
        tag, prefix, secret = credential.split("_", 2)
    except (AttributeError, ValueError):
        return None, None
    if tag != "mnpdev":
        return None, None
    dev = AgentDevice.objects.filter(token_prefix=prefix).first()
    if not dev or not dev.check_secret(secret):
        return None, None
    return dev, secret


def issue_access_token(device):
    return _signer.sign(f"{device.pk}:{device.token_version}:{secrets.token_hex(8)}")


def device_from_access_token(token):
    try:
        raw = _signer.unsign(token, max_age=ACCESS_TOKEN_TTL)
        dev_id, version, _ = raw.split(":")
    except (signing.BadSignature, signing.SignatureExpired, ValueError):
        return None
    dev = AgentDevice.objects.filter(pk=dev_id, is_revoked=False).first()
    if not dev or str(dev.token_version) != version:
        return None
    return dev


def agent_error(code, http_status, **extra):
    return JsonResponse({"ok": False, "error": code, **extra}, status=http_status)


def _store_nonce(device, nonce):
    from django.db import IntegrityError, transaction
    from .models import AgentNonce
    try:
        with transaction.atomic():
            AgentNonce.objects.create(device=device, nonce=nonce)
    except IntegrityError:
        return False
    if secrets.randbelow(100) == 0:  # occasional cleanup; tokens live 15 min, keep nonces for 1 h
        AgentNonce.objects.filter(created_at__lt=timezone.now() - timedelta(hours=1)).delete()
    return True


def agent_required(view):
    """Bearer short-lived access token + kill switch + rate limit + replay protection on writes."""
    @functools.wraps(view)
    def wrapper(request, *args, **kwargs):
        if HubSettings.get().kill_switch:
            return agent_error("kill_switch_active", 423)
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        device = device_from_access_token(auth[7:]) if auth.startswith("Bearer ") else None
        if not device:
            return agent_error("unauthorized", 401)
        if rate_limited(f"dev:{device.pk}", getattr(settings, "HUB_AGENT_RATE_LIMIT", 120), 60):
            audit("agent_rate_limited", request=request, device=device, outcome="denied")
            return agent_error("rate_limited", 429)
        if request.method != "GET":
            nonce = request.META.get("HTTP_X_REQUEST_ID", "")
            if not (16 <= len(nonce) <= 80):
                return agent_error("missing_request_id", 400)
            if not _store_nonce(device, nonce):
                audit("agent_replay_blocked", request=request, device=device, outcome="denied")
                return agent_error("replayed_request", 409)
        AgentDevice.objects.filter(pk=device.pk).update(last_heartbeat=timezone.now(), last_ip=client_ip(request))
        request.agent_device = device
        return view(request, *args, **kwargs)
    return wrapper
