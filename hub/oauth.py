"""
OAuth 2.0 authorization-code flow with state + PKCE (S256), least-privilege scopes,
encrypted token storage and revocation. Provider credentials come from env only.
"""
import base64
import hashlib
import secrets
import time
from datetime import timedelta
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.utils import timezone

from .crypto import sha256_hex
from .models import ConnectedAccount, IntegrationToken

STATE_TTL = 600
SESSION_KEY = "hub_oauth_pending"

PROVIDERS = {
    "github": dict(authorize="https://github.com/login/oauth/authorize",
                   token="https://github.com/login/oauth/access_token",
                   scopes=["read:user"], pkce=True, revoke="github"),
    "gitlab": dict(authorize="https://gitlab.com/oauth/authorize", token="https://gitlab.com/oauth/token",
                   scopes=["read_user"], pkce=True, revoke="https://gitlab.com/oauth/revoke"),
    "google": dict(authorize="https://accounts.google.com/o/oauth2/v2/auth", token="https://oauth2.googleapis.com/token",
                   scopes=["openid", "email", "profile"], pkce=True, revoke="https://oauth2.googleapis.com/revoke",
                   extra={"access_type": "offline", "prompt": "consent"}),
}


class OAuthError(Exception):
    pass


def credentials(key):
    cid = getattr(settings, f"HUB_OAUTH_{key.upper()}_CLIENT_ID", "") or ""
    secret = getattr(settings, f"HUB_OAUTH_{key.upper()}_CLIENT_SECRET", "") or ""
    return cid, secret


def configured(key):
    return key in PROVIDERS and all(credentials(key))


def redirect_uri(key):
    return f"{settings.SITE_URL.rstrip('/')}/hub/accounts/oauth/{key}/callback/"


def start(request, account):
    key = account.provider.connector
    if not configured(key):
        raise OAuthError("provider_not_configured")
    cfg = PROVIDERS[key]
    state = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    pending = request.session.get(SESSION_KEY, {})
    # keep only fresh entries; store a hash of the state, never the raw value as a key
    pending = {k: v for k, v in pending.items() if v["exp"] > time.time()}
    pending[sha256_hex(state)] = {"account": account.pk, "provider": key, "verifier": verifier, "exp": time.time() + STATE_TTL}
    request.session[SESSION_KEY] = pending
    params = {"client_id": credentials(key)[0], "redirect_uri": redirect_uri(key), "response_type": "code",
              "scope": " ".join(cfg["scopes"]), "state": state, **cfg.get("extra", {})}
    if cfg["pkce"]:
        params.update(code_challenge=challenge, code_challenge_method="S256")
    return f"{cfg['authorize']}?{urlencode(params)}"


def finish(request, key, *, state, code, error=""):
    """Validates state (single-use, bound to this session + provider), exchanges the code, stores tokens."""
    pending = request.session.get(SESSION_KEY, {})
    entry = pending.pop(sha256_hex(state or ""), None)
    request.session[SESSION_KEY] = pending
    if not entry or entry["exp"] < time.time() or entry["provider"] != key:
        raise OAuthError("invalid_state")
    account = ConnectedAccount.objects.filter(pk=entry["account"], provider__connector=key).first()
    if not account:
        raise OAuthError("account_not_found")
    if error or not code:
        account.status, account.last_error, account.last_failure_at = "error", f"authorization_denied:{error[:60]}", timezone.now()
        account.save()
        raise OAuthError("authorization_denied")
    cid, secret = credentials(key)
    data = {"client_id": cid, "client_secret": secret, "code": code, "redirect_uri": redirect_uri(key),
            "grant_type": "authorization_code", "code_verifier": entry["verifier"]}
    try:
        r = requests.post(PROVIDERS[key]["token"], data=data, headers={"Accept": "application/json"}, timeout=15)
        payload = r.json()
    except (requests.RequestException, ValueError) as exc:
        raise OAuthError("token_exchange_failed") from exc
    if r.status_code != 200 or "access_token" not in payload:
        account.status, account.last_error, account.last_failure_at = "error", "token_exchange_failed", timezone.now()
        account.save()
        raise OAuthError("token_exchange_failed")
    expires = timezone.now() + timedelta(seconds=int(payload["expires_in"])) if payload.get("expires_in") else None
    IntegrationToken.store(account, "access", payload["access_token"], expires)
    if payload.get("refresh_token"):
        IntegrationToken.store(account, "refresh", payload["refresh_token"])
    granted = payload.get("scope", " ".join(PROVIDERS[key]["scopes"]))
    account.scopes = [s for s in granted.replace(",", " ").split() if s]
    account.status, account.last_error, account.required_action = "connected", "", ""
    account.last_success_at = timezone.now()
    account.save()
    return account


def revoke(account):
    """Revoke at the provider when supported, then invalidate local ciphertext. Returns provider_result."""
    key = account.provider.connector
    result = "no_tokens"
    token = account.token("refresh") or account.token("access")
    if token and key in PROVIDERS and configured(key):
        cid, secret = credentials(key)
        try:
            target = PROVIDERS[key]["revoke"]
            if target == "github":
                r = requests.delete(f"https://api.github.com/applications/{cid}/grant", auth=(cid, secret),
                                    json={"access_token": account.token("access")}, timeout=15,
                                    headers={"Accept": "application/vnd.github+json"})
            else:
                r = requests.post(target, data={"token": token, "client_id": cid, "client_secret": secret}, timeout=15)
            result = "revoked_at_provider" if r.status_code in (200, 204) else f"provider_http_{r.status_code}"
        except requests.RequestException:
            result = "provider_unreachable"
    elif token:
        result = "provider_not_configured_local_only"
    now = timezone.now()
    account.tokens.filter(revoked_at__isnull=True).update(revoked_at=now)
    account.tokens.update(ciphertext="")  # remove ciphertext entirely
    account.status, account.permissions, account.required_action = "revoked", {}, "Reconnect to use this account again"
    account.save()
    return result
