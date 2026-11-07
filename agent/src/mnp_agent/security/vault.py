"""
Local secret vault. Uses the OS keyring — on Windows that is Windows Credential Manager
(protected by DPAPI for the logged-in user). There is NO plaintext fallback.
"""
SERVICE = "mohamed-nabil-ai-hub"


class VaultError(Exception):
    pass


def _keyring():
    try:
        import keyring
        from keyring.backends import fail
    except ImportError as exc:  # pragma: no cover
        raise VaultError("Install the 'keyring' package") from exc
    if isinstance(keyring.get_keyring(), fail.Keyring):
        raise VaultError("No secure OS keyring available; refusing to store secrets in plain text")
    return keyring


def save_credential(server_url, credential):
    if not credential.startswith("mnpdev_") or credential.count("_") < 2:
        raise VaultError("That does not look like a device credential (mnpdev_…)")
    _keyring().set_password(SERVICE, server_url, credential)


def load_credential(server_url):
    cred = _keyring().get_password(SERVICE, server_url)
    if not cred:
        raise VaultError("No device credential stored. Run: mnp-agent login")
    return cred


def delete_credential(server_url):
    try:
        _keyring().delete_password(SERVICE, server_url)
    except Exception:
        pass
