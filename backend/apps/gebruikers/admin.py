"""Admin configuratie voor gebruikers."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "naam", "organisatie", "rol", "status", "is_active", "totp_enabled")
    list_filter = ("rol", "status", "is_active", "totp_enabled")
    search_fields = ("email", "naam")
    ordering = ("-aangemaakt_op",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Persoonlijke informatie", {"fields": ("naam", "telefoon", "organisatie")}),
        ("Rollen en status", {"fields": ("rol", "status", "totp_enabled")}),
        ("Permissies", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "naam", "password1", "password2", "organisatie", "rol"),
            },
        ),
    )
