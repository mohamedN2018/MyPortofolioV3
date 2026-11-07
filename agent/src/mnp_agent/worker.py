"""Heartbeat + task loop. Executes only allowlisted tools; checks for cancellation."""
import logging
import time

from .client import HubError
from .connectors.browser_handoff import HandoffRefused, open_application_page
from .tools.registry import LOCAL_TOOLS, TaskRejected, validate_task

log = logging.getLogger("mnp_agent")


def execute(client, config, task):
    tid = task.get("id")
    try:
        tool, payload = validate_task(task)
    except TaskRejected as exc:
        log.warning("task %s rejected locally: %s", tid, exc)
        client.complete(tid, "failed", error=f"rejected_by_agent:{exc}")
        return "rejected"
    client.progress(tid, 10, f"running {tool}")
    try:
        if tool in LOCAL_TOOLS:
            result = open_application_page(client, payload, config)
        else:
            result = client.call(tool, payload)
    except (HubError, HandoffRefused) as exc:
        code = getattr(exc, "code", str(exc))
        log.warning("task %s failed: %s", tid, code)
        client.complete(tid, "failed", error=str(code))
        return "failed"
    if client.progress(tid, 90, "reporting result").get("cancel"):
        client.complete(tid, "cancelled", error="cancelled_by_owner")
        return "cancelled"
    summary = {"keys": sorted(result)} if isinstance(result, dict) else {}
    client.complete(tid, "succeeded", result=summary)
    return "succeeded"


def run(client, config, stop=lambda: False, sleep=time.sleep):
    last_beat = 0.0
    backoff = config.poll_seconds
    while not stop():
        try:
            if time.time() - last_beat >= config.heartbeat_seconds:
                client.heartbeat("idle")
                last_beat = time.time()
            task = client.next_task()
            if task:
                log.info("task %s: %s", task.get("id"), task.get("tool"))
                execute(client, config, task)
                continue
            backoff = config.poll_seconds
        except HubError as exc:
            if exc.code == "kill_switch_active":
                log.error("kill switch is active on the server — pausing")
                backoff = min(backoff * 2, 600)
            elif exc.status == 401 and exc.code == "invalid_device_credential":
                log.error("device credential rejected (revoked or rotated). Run `mnp-agent login` with a new credential.")
                return 2
            else:
                log.warning("server error: %s", exc.code)
                backoff = min(backoff * 2, 300)
        except Exception as exc:  # network errors etc. — never crash-loop fast
            log.warning("connection problem: %s", exc.__class__.__name__)
            backoff = min(backoff * 2, 300)
        sleep(backoff)
    return 0
