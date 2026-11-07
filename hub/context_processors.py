def hub(request):
    """Only for owner pages under /hub/ — public pages get nothing (no queries, no data)."""
    if not request.path.startswith("/hub/") or not getattr(request, "user", None) or not request.user.is_superuser:
        return {}
    from django.conf import settings
    from .models import AgentDevice, ApprovalRequest, HubSettings
    return {"site_version": getattr(settings, "SITE_VERSION", ""),"hub_kill": HubSettings.get().kill_switch,
            "hub_pending": ApprovalRequest.objects.filter(status="pending").count(),
            "hub_online": sum(1 for d in AgentDevice.objects.filter(is_revoked=False) if d.online)}
