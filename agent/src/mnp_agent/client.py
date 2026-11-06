"""
Outbound HTTPS client for the hub. Never opens a listening socket.

- Exchanges the device credential (from the OS vault) for a 15-minute access token.
- Adds a unique X-Request-Id to every write (server-side replay protection).
- Does not hammer the server: one token refresh per 401, then stops.
"""
import secrets
import time

import requests

from . import __version__


class HubError(Exception):
    def __init__(self, code, status=None, payload=None):
        super().__init__(code)
        self.code, self.status, self.payload = code, status, payload or {}


class HubClient:
    def __init__(self, server_url, credential_loader, session=None, timeout=20):
        self.base = server_url.rstrip("/") + "/hub/api/agent"
        self._load_credential = credential_loader
        self.http = session or requests.Session()
        self.http.headers["User-Agent"] = f"mnp-agent/{__version__}"
        self.timeout = timeout
        self._token, self._token_exp = None, 0.0

    # -------------------------------------------------------------- auth
    def _authenticate(self):
        r = self.http.post(f"{self.base}/token/", headers={"Authorization": f"Device {self._load_credential()}"},
                           timeout=self.timeout, allow_redirects=False)
        data = self._decode(r)
        self._token = data["access_token"]
        self._token_exp = time.time() + int(data.get("expires_in", 900)) - 60
        return data

    def _ensure_token(self):
        if not self._token or time.time() >= self._token_exp:
            self._authenticate()

    def forget_token(self):
        self._token, self._token_exp = None, 0.0

    @staticmethod
    def _decode(r):
        try:
            data = r.json()
        except ValueError:
            raise HubError("invalid_server_response", r.status_code)
        if r.status_code >= 400 or not data.get("ok"):
            raise HubError(data.get("error", f"http_{r.status_code}"), r.status_code, data)
        return data

    def _request(self, method, path, json_body=None, retry=True):
        self._ensure_token()
        headers = {"Authorization": f"Bearer {self._token}"}
        if method != "GET":
            headers["X-Request-Id"] = secrets.token_hex(16)
        r = self.http.request(method, f"{self.base}/{path}", json=json_body, headers=headers,
                              timeout=self.timeout, allow_redirects=False)
        if r.status_code == 401 and retry:
            self.forget_token()
            return self._request(method, path, json_body, retry=False)
        return self._decode(r)

    # -------------------------------------------------------------- API
    def heartbeat(self, note=""):
        return self._request("POST", "heartbeat/", {"version": __version__, "note": note[:200]})

    def tools(self):
        return self._request("GET", "tools/")["tools"]

    def call(self, tool, args=None):
        return self._request("POST", f"tools/{tool}/", args or {})["result"]

    def next_task(self):
        return self._request("GET", "tasks/next/")["task"]

    def progress(self, task_id, progress, message=""):
        return self._request("POST", f"tasks/{task_id}/progress/", {"progress": progress, "message": message[:500]})

    def complete(self, task_id, status, result=None, error=""):
        return self._request("POST", f"tasks/{task_id}/complete/", {"status": status, "result": result or {}, "error": error[:500]})
