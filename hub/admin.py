from django.contrib import admin

from .models import AuditEvent, Provider


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    """Read-only: the audit log can't be edited or deleted from the admin."""
    list_display = ("created_at", "actor_type", "actor_label", "action", "level", "outcome")
    list_filter = ("actor_type", "level", "outcome")
    search_fields = ("action", "actor_label")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "connector", "reviewed_at")
