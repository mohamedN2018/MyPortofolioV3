"""Local log with secret redaction (device credentials and bearer tokens never reach disk)."""
import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path

_PATTERNS = [re.compile(r"mnpdev_[A-Za-z0-9]+_[A-Za-z0-9_\-]+"), re.compile(r"(Bearer|Device)\s+[A-Za-z0-9:._\-]+"),
             re.compile(r"(?i)(password|token|secret|cookie)=\S+")]


def redact(text):
    s = str(text)
    for p in _PATTERNS:
        s = p.sub("[redacted]", s)
    return s


class RedactingFilter(logging.Filter):
    def filter(self, record):
        record.msg = redact(record.getMessage())
        record.args = ()
        return True


def setup(log_file):
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger("mnp_agent")
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    fh = RotatingFileHandler(log_file, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    for h in (fh, sh):
        h.addFilter(RedactingFilter())
        log.addHandler(h)
    return log
