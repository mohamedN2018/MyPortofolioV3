"""
User-assisted workflow: open the OFFICIAL application page in the user's own browser.

No automation of the page, no cookie or session access, no form filling, no CAPTCHA
handling. The user reviews and submits; the agent then records the real outcome.
"""
import webbrowser
from urllib.parse import urlsplit


class HandoffRefused(Exception):
    pass


def check_url(url, allowed_hosts=()):
    u = urlsplit(url or "")
    if u.scheme != "https" or not u.hostname:
        raise HandoffRefused("only https URLs are opened")
    if u.username or u.password:
        raise HandoffRefused("URLs with embedded credentials are refused")
    if allowed_hosts and not any(u.hostname == h or u.hostname.endswith("." + h) for h in allowed_hosts):
        raise HandoffRefused(f"host not in allowed_apply_hosts: {u.hostname}")
    return url


def open_application_page(client, payload, config, opener=webbrowser.open):
    """Opens the apply URL of an application that the owner has APPROVED (status 'ready')."""
    if not config.allow_open_browser:
        raise HandoffRefused("allow_open_browser is disabled in config")
    app_id = payload.get("application_id")
    app = client.call("get_application", {"application_id": app_id})["application"]
    if app["status"] != "ready":
        raise HandoffRefused(f"application is '{app['status']}', not approved/ready")
    url = check_url(app["apply_url"], config.allowed_apply_hosts)
    opener(url, new=2)
    return {"opened": url, "next": "Submit on the official page yourself, then record the result with evidence."}
