"""
Agent API (JSON). The local agent only ever makes OUTBOUND HTTPS calls here.

POST /hub/api/agent/token/                 device credential -> 15-min access token
POST /hub/api/agent/heartbeat/             online status
GET  /hub/api/agent/tools/                 allowlisted tools + levels
POST /hub/api/agent/tools/<name>/          run one tool (JSON object body)
GET  /hub/api/agent/tasks/next/            next owner-assigned task for this device
POST /hub/api/agent/tasks/<id>/progress/   progress + log line (returns cancel flag)
POST /hub/api/agent/tasks/<id>/complete/   final status + result
GET  /hub/api/agent/cv/<id>/download/      a CV file (needs get_cv_versions enabled)
"""
import json

from django.db import transaction
from django.http import FileResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from . import tools
from .models import AgentTask, CVDocument, HubSettings
from .security import (agent_error, agent_required, audit, client_ip, issue_access_token, parse_device_credential,
                       rate_limited, ACCESS_TOKEN_TTL)

MAX_BODY = 256 * 1024


def _json(request):
    if len(request.body) > MAX_BODY:
        raise ValueError("body_too_large")
    data = json.loads(request.body or b"{}")
    if not isinstance(data, dict):
        raise ValueError("body_must_be_object")
    return data


def _ok(**data):
    return JsonResponse({"ok": True, **data}, json_dumps_params={"default": str})


@csrf_exempt  # bearer-credential API, no cookies involved
@require_POST
def token(request):
    ip = client_ip(request) or "unknown"
    if rate_limited(f"agent-token:{ip}", 10, 300):
        return agent_error("rate_limited", 429)
    if HubSettings.get().kill_switch:
        return agent_error("kill_switch_active", 423)
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    device, _ = parse_device_credential(auth[7:]) if auth.startswith("Device ") else (None, None)
    if not device or device.is_revoked:
        audit("agent_auth_failed", request=request, outcome="denied")
        return agent_error("invalid_device_credential", 401)
    audit("agent_token_issued", request=request, device=device)
    return _ok(access_token=issue_access_token(device), expires_in=ACCESS_TOKEN_TTL, device={"id": device.pk, "name": device.name})


@csrf_exempt
@require_POST
@agent_required
def heartbeat(request):
    dev = request.agent_device
    try:
        data = _json(request)
    except ValueError as exc:
        return agent_error(str(exc) if str(exc).startswith("body") else "invalid_json", 400)
    dev.agent_version = str(data.get("version", ""))[:40]
    dev.status_note = str(data.get("note", ""))[:200]
    dev.save(update_fields=["agent_version", "status_note"])
    return _ok(server_time=timezone.now(), kill_switch=False)


@require_GET
@agent_required
def tool_list(request):
    dev = request.agent_device
    return _ok(tools=[{**t, "enabled": t.get("local") or tools.tool_enabled(dev, t["name"])} for t in tools.describe()])


@csrf_exempt
@require_POST
@agent_required
def tool_call(request, name):
    try:
        args = _json(request)
    except ValueError as exc:
        return agent_error(str(exc) if str(exc).startswith("body") else "invalid_json", 400)
    try:
        result = tools.run(request.agent_device, name, args, request=request)
    except tools.ToolError as exc:
        return agent_error(exc.code, exc.status, **exc.extra)
    return _ok(tool=name, result=result)


@require_GET
@agent_required
def next_task(request):
    dev = request.agent_device
    with transaction.atomic():
        task = (AgentTask.objects.select_for_update(skip_locked=True)
                .filter(device=dev, initiator="user", status="queued", cancel_requested=False).order_by("created_at").first())
        if not task:
            return _ok(task=None)
        task.status, task.started_at = "running", timezone.now()
        task.add_log("picked up by agent", save=False)
        task.save()
    audit("task_started", request=request, device=dev, level=task.level, target=task)
    return _ok(task={"id": str(task.id), "tool": task.tool, "level": task.level, "payload": task.payload})


def _own_task(request, task_id):
    return AgentTask.objects.filter(pk=task_id, device=request.agent_device).first()


@csrf_exempt
@require_POST
@agent_required
def task_progress(request, task_id):
    task = _own_task(request, task_id)
    if not task:
        return agent_error("task_not_found", 404)
    try:
        data = _json(request)
    except ValueError:
        return agent_error("invalid_json", 400)
    if task.finished:
        return _ok(cancel=True, status=task.status)
    task.progress = max(0, min(100, int(data.get("progress", task.progress) or 0)))
    if data.get("message"):
        task.add_log(data["message"], save=False)
    task.save(update_fields=["progress", "log"])
    return _ok(cancel=task.cancel_requested)


@csrf_exempt
@require_POST
@agent_required
def task_complete(request, task_id):
    task = _own_task(request, task_id)
    if not task:
        return agent_error("task_not_found", 404)
    if task.finished:
        return agent_error("task_already_finished", 409, status=task.status)
    try:
        data = _json(request)
    except ValueError:
        return agent_error("invalid_json", 400)
    status = data.get("status")
    if status not in ("succeeded", "failed", "cancelled"):
        return agent_error("invalid_status", 400)
    task.status, task.finished_at, task.progress = status, timezone.now(), 100 if status == "succeeded" else task.progress
    task.result = data.get("result") if isinstance(data.get("result"), dict) else {}
    task.error = str(data.get("error", ""))[:500]
    task.add_log(f"finished: {status}", save=False)
    task.save()
    audit("task_finished", request=request, device=request.agent_device, level=task.level, target=task,
          outcome="ok" if status == "succeeded" else "error")
    return _ok(status=task.status)


@require_GET
@agent_required
def cv_download(request, pk):
    dev = request.agent_device
    if not tools.tool_enabled(dev, "get_cv_versions"):
        return agent_error("tool_disabled_for_device", 403)
    cv = CVDocument.objects.filter(pk=pk, is_active=True).exclude(file="").first()
    if not cv:
        return agent_error("cv_not_found", 404)
    audit("cv_downloaded", request=request, device=dev, target=cv)
    return FileResponse(cv.file.open("rb"), as_attachment=True, filename=cv.file.name.rsplit("/", 1)[-1])
