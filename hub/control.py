"""Owner-side controls: kill switch and executing approved critical actions."""
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from . import oauth
from .models import AgentDevice, AgentTask, ApprovalRequest, ConnectedAccount, HubSettings
from .security import audit


@transaction.atomic
def activate_kill_switch(request, reason=""):
    hs = HubSettings.get()
    hs.kill_switch, hs.kill_switch_at, hs.kill_switch_reason = True, timezone.now(), reason[:300]
    hs.save()
    AgentDevice.objects.update(token_version=F("token_version") + 1)           # every access token dies now
    cancelled = AgentTask.objects.filter(status__in=["queued", "running", "awaiting_approval"]).update(
        status="cancelled", cancel_requested=True, error="kill_switch", finished_at=timezone.now())
    expired = ApprovalRequest.objects.filter(status__in=["pending", "approved"]).update(status="expired")
    for acc in ConnectedAccount.objects.all():                                  # external permissions off
        if acc.permissions.get("submit") or acc.permissions.get("write"):
            acc.permissions = {**acc.permissions, "submit": False, "write": False}
            acc.save(update_fields=["permissions"])
    audit("kill_switch_on", request=request, level="critical", tasks_cancelled=cancelled, approvals_expired=expired, reason=reason[:300])
    return cancelled, expired


def deactivate_kill_switch(request):
    hs = HubSettings.get()
    hs.kill_switch = False
    hs.save(update_fields=["kill_switch", "updated_at"])
    audit("kill_switch_off", request=request, level="critical")


def disable_job_connections(request):
    """Emergency button on /hub/accounts/jobs/: all job accounts lose every permission; pending agent tasks stop."""
    n = 0
    for acc in ConnectedAccount.objects.exclude(provider__category__in=["developer", "google"]):
        acc.permissions, acc.status = {}, "disconnected"
        acc.required_action = "Re-enable permissions after the emergency stop"
        acc.save(update_fields=["permissions", "status", "required_action"])
        n += 1
    stopped = AgentTask.objects.filter(status__in=["queued", "running"]).update(status="cancelled", cancel_requested=True,
                                                                                 error="job_connections_disabled", finished_at=timezone.now())
    audit("job_connections_disabled", request=request, level="critical", accounts=n, tasks_stopped=stopped)
    return n, stopped


def execute_critical(request, appr):
    """Runs an approved CRITICAL request immediately (owner action)."""
    acc = ConnectedAccount.objects.filter(pk=appr.payload.get("account_id")).first()
    if not acc:
        return "account_missing"
    if appr.action == "change_account_permission":
        perm, enable = appr.payload["permission"], bool(appr.payload["enable"])
        if perm == "submit" and enable and not acc.provider.can_submit:
            return "provider_does_not_support_submission"
        acc.permissions = {**acc.permissions, perm: enable}
        acc.save(update_fields=["permissions"])
        result = "permission_updated"
    elif appr.action == "disconnect_account":
        acc.status, acc.permissions = "disconnected", {}
        acc.save(update_fields=["status", "permissions"])
        result = "disconnected"
    elif appr.action == "revoke_account":
        result = oauth.revoke(acc)
    else:
        return "unknown_action"
    appr.status, appr.consumed_at = "executed", timezone.now()
    appr.save(update_fields=["status", "consumed_at"])
    audit(f"approval_executed:{appr.action}", request=request, level="critical", target=acc, result=result)
    return result
