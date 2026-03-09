"""Admin registraties voor core app."""

from django.contrib import admin

from .audit import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Read-only audit log overzicht in de Django Admin."""

    list_display = [
        "tijdstip",
        "actor_email",
        "actie",
        "object_type",
        "object_omschrijving_kort",
        "ip_adres",
    ]
    list_filter = ["actie", "object_type", "tijdstip"]
    search_fields = ["actor_email", "object_omschrijving", "object_id", "ip_adres"]
    readonly_fields = [
        "actor_id",
        "actor_email",
        "actie",
        "object_type",
        "object_id",
        "object_omschrijving",
        "wijzigingen",
        "extra",
        "ip_adres",
        "user_agent",
        "tijdstip",
    ]
    ordering = ["-tijdstip"]
    date_hierarchy = "tijdstip"

    # Geen aanmaken/bewerken/verwijderen vanuit admin
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Object")
    def object_omschrijving_kort(self, obj):
        return obj.object_omschrijving[:60] + ("…" if len(obj.object_omschrijving) > 60 else "")
