"""
Encryption at rest for integration tokens and MFA secrets.

Key management:
- HUB_ENCRYPTION_KEYS (env) = comma-separated Fernet keys, newest first.
  New data is encrypted with the first key; older keys still decrypt, so keys
  can be rotated without downtime (`manage.py hub_rotate_keys` re-encrypts).
- If unset, a key is *derived* from SECRET_KEY so local development works.
  Production must set HUB_ENCRYPTION_KEYS explicitly (checked by `hub_check`).

Plaintext secrets never leave this module except to the integration service
that needs them; they are never logged, rendered, or returned by any API.
"""
import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from django.conf import settings


def _keys():
    raw = getattr(settings, "HUB_ENCRYPTION_KEYS", "") or ""
    keys = [k.strip() for k in raw.split(",") if k.strip()]
    if not keys:
        digest = hashlib.sha256(("hub-dev-key:" + settings.SECRET_KEY).encode()).digest()
        keys = [base64.urlsafe_b64encode(digest).decode()]
    return [Fernet(k.encode()) for k in keys]


def explicit_key_configured() -> bool:
    return bool((getattr(settings, "HUB_ENCRYPTION_KEYS", "") or "").strip())


def encrypt(plaintext: str) -> str:
    if plaintext is None or plaintext == "":
        return ""
    return MultiFernet(_keys()).encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    if not ciphertext:
        return ""
    try:
        return MultiFernet(_keys()).decrypt(ciphertext.encode()).decode()
    except InvalidToken as exc:  # wrong/rotated-out key or tampering
        raise ValueError("Unable to decrypt secret (key missing or data tampered)") from exc


def rotate(ciphertext: str) -> str:
    """Re-encrypt with the newest key."""
    if not ciphertext:
        return ""
    return MultiFernet(_keys()).rotate(ciphertext.encode()).decode()


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
