def hub(request):
    """Only for owner pages under /hub/ — public pages get nothing (no queries, no data)."""
    if not request.path.startswith("/hub/") or not getattr(request, "user", None) or not request.user.is_superuser:
        return {}
    from .models import AgentDevice, ApprovalRequest, HubSettings
    return {"hub_kill": HubSettings.get().kill_switch,
            "hub_pending": ApprovalRequest.objects.filter(status="pending").count(),
            "hub_online": sum(1 for d in AgentDevice.objects.filter(is_revoked=False) if d.online)}
