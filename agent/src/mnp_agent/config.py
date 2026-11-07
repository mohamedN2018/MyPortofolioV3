"""Agent configuration (no secrets in this file — the device credential lives in the OS vault)."""
import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

DEFAULT_PATH = Path(os.environ.get("MNP_AGENT_CONFIG", Path.home() / ".mnp-agent" / "config.yaml"))


class ConfigError(Exception):
    pass


@dataclass
class Config:
    server_url: str
    device_name: str = "Windows PC"
    poll_seconds: int = 20
    heartbeat_seconds: int = 30
    allow_open_browser: bool = True
    allowed_apply_hosts: list = field(default_factory=list)  # empty = any https host from an approved application
    log_file: str = str(Path.home() / ".mnp-agent" / "agent.log")

    def validate(self):
        u = urlsplit(self.server_url)
        local = u.hostname in ("127.0.0.1", "localhost")
        if u.scheme != "https" and not (local and u.scheme == "http"):
            raise ConfigError("server_url must use https:// (http is only allowed for localhost development)")
        if u.path not in ("", "/") or u.query:
            raise ConfigError("server_url must be the site root, e.g. https://mohamednabilpro.deplois.net")
        self.server_url = f"{u.scheme}://{u.netloc}"
        self.poll_seconds = max(5, int(self.poll_seconds))
        self.heartbeat_seconds = max(10, int(self.heartbeat_seconds))
        return self


def load(path=None):
    import yaml
    p = Path(path or DEFAULT_PATH)
    if not p.exists():
        raise ConfigError(f"Config not found: {p}. Copy config.example.yaml there.")
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    for forbidden in ("credential", "token", "password", "secret", "cookie"):
        if any(forbidden in k.lower() for k in data):
            raise ConfigError(f"Secrets must not be stored in the config file (found '{forbidden}'). Use `mnp-agent login`.")
    known = {k: v for k, v in data.items() if k in Config.__dataclass_fields__}
    if "server_url" not in known:
        raise ConfigError("server_url is required")
    return Config(**known).validate()
