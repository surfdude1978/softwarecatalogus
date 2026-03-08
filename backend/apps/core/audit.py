"""Audit logging voor de Softwarecatalogus.

Logt alle schrijfacties (aanmaken, bijwerken, verwijderen) op alle
ViewSet endpoints, inclusief actor, IP-adres en gewijzigde velden.

Gebruik:
    class MijnViewSet(AuditLogMixin, viewsets.ModelViewSet):
        ...
"""
import json
import logging

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger("softwarecatalogus.audit")


# ── Model ────────────────────────────────────────────────────────────────────

class AuditLog(models.Model):
    """Registratie van elke schrijfactie in de applicatie."""

    class Actie(models.TextChoices):
        AANGEMAAKT = "aangemaakt", _("Aangemaakt")
        BIJGEWERKT = "bijgewerkt", _("Bijgewerkt")
        VERWIJDERD = "verwijderd", _("Verwijderd")
        INGELOGD   = "ingelogd",   _("Ingelogd")
        UITGELOGD  = "uitgelogd",  _("Uitgelogd")
        EXPORT     = "export",     _("Export")
        IMPORT     = "import",     _("Import")
        GEFIATEERD = "gefiateerd", _("Gefiateerd")

    # Wie
    actor_id = models.CharField(
        max_length=36, blank=True, null=True,
        help_text="UUID van de gebruiker die de actie uitvoerde (null = anoniem)."
    )
    actor_email = models.EmailField(
        blank=True,
        help_text="E-mailadres ten tijde van de actie (voor historische referentie)."
    )

    # Wat
    actie = models.CharField(max_length=20, choices=Actie.choices)
    object_type = models.CharField(
        max_length=100,
        help_text="Type object waarop de actie werd uitgevoerd (bijv. 'Pakket')."
    )
    object_id = models.CharField(
        max_length=36, blank=True, null=True,
        help_text="UUID of PK van het object."
    )
    object_omschrijving = models.CharField(
        max_length=500, blank=True,
        help_text="Leesbare omschrijving van het object (bijv. naam)."
    )

    # Details
    wijzigingen = models.JSONField(
        default=dict, blank=True,
        help_text="Dict van gewijzigde velden: {'veld': {'oud': ..., 'nieuw': ...}}."
    )
    extra = models.JSONField(
        default=dict, blank=True,
        help_text="Aanvullende context (endpoint, parameters, etc.)."
    )

    # Technisch
    ip_adres = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    tijdstip = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-tijdstip"]
        verbose_name = "Auditlog"
        verbose_name_plural = "Auditlogs"
        indexes = [
            models.Index(fields=["actor_id", "-tijdstip"]),
            models.Index(fields=["object_type", "object_id"]),
            models.Index(fields=["actie", "-tijdstip"]),
        ]

    def __str__(self):
        return f"{self.tijdstip:%Y-%m-%d %H:%M} | {self.actor_email or 'anoniem'} | {self.actie} | {self.object_type} #{self.object_id}"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_ip(request) -> str | None:
    """Haal het IP-adres op van de request (proxy-aware)."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _get_object_info(instance) -> tuple[str, str, str]:
    """Retourneer (object_type, object_id, omschrijving) voor een model instance."""
    object_type = type(instance).__name__
    object_id = str(getattr(instance, "pk", "") or "")
    # Probeer naam of __str__ als omschrijving
    omschrijving = str(
        getattr(instance, "naam", None)
        or getattr(instance, "title", None)
        or getattr(instance, "email", None)
        or str(instance)
    )[:500]
    return object_type, object_id, omschrijving


def log_actie(
    request,
    actie: str,
    instance=None,
    object_type: str = "",
    object_id: str = "",
    object_omschrijving: str = "",
    wijzigingen: dict | None = None,
    extra: dict | None = None,
) -> AuditLog:
    """Sla een auditlog entry op.

    Args:
        request: De HTTP-request (voor actor en IP).
        actie: Eén van AuditLog.Actie waarden.
        instance: Django model instance (optioneel; vervangt object_* params).
        object_type: Naam van het object type (als geen instance).
        object_id: PK van het object (als geen instance).
        object_omschrijving: Leesbare omschrijving (als geen instance).
        wijzigingen: Dict van {'veld': {'oud': ..., 'nieuw': ...}}.
        extra: Aanvullende context.

    Returns:
        Opgeslagen AuditLog instance.
    """
    if instance is not None:
        object_type, object_id, object_omschrijving = _get_object_info(instance)

    user = getattr(request, "user", None)
    actor_id = str(user.pk) if user and user.is_authenticated else None
    actor_email = getattr(user, "email", "") if user and user.is_authenticated else ""

    entry = AuditLog.objects.create(
        actor_id=actor_id,
        actor_email=actor_email,
        actie=actie,
        object_type=object_type,
        object_id=object_id,
        object_omschrijving=object_omschrijving,
        wijzigingen=wijzigingen or {},
        extra=extra or {},
        ip_adres=_get_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
    )

    # Schrijf ook naar Python logger voor centrale log-aggregatie
    logger.info(
        "AUDIT | %s | %s | %s | %s #%s | IP=%s",
        entry.tijdstip.isoformat(),
        actor_email or "anoniem",
        actie,
        object_type,
        object_id,
        _get_ip(request),
    )

    return entry


# ── Mixin ────────────────────────────────────────────────────────────────────

class AuditLogMixin:
    """ViewSet mixin die automatisch audit logs aanmaakt bij schrijfacties.

    Gebruik:
        class MijnViewSet(AuditLogMixin, viewsets.ModelViewSet):
            ...
    """

    def perform_create(self, serializer):
        instance = serializer.save()
        log_actie(
            self.request,
            AuditLog.Actie.AANGEMAAKT,
            instance=instance,
        )
        return instance

    def perform_update(self, serializer):
        # Vang oude waarden op vóór update
        instance = serializer.instance
        oude_data = {}
        for field in serializer.validated_data:
            oude_waarde = getattr(instance, field, None)
            if hasattr(oude_waarde, "pk"):
                oude_waarde = str(oude_waarde.pk)
            elif hasattr(oude_waarde, "__iter__") and not isinstance(oude_waarde, str):
                oude_waarde = list(map(str, oude_waarde))
            oude_data[field] = oude_waarde

        instance = serializer.save()

        wijzigingen = {}
        for field, oud in oude_data.items():
            nieuw = getattr(instance, field, None)
            if hasattr(nieuw, "pk"):
                nieuw = str(nieuw.pk)
            elif hasattr(nieuw, "__iter__") and not isinstance(nieuw, str):
                nieuw = list(map(str, nieuw))
            if str(oud) != str(nieuw):
                wijzigingen[field] = {"oud": str(oud), "nieuw": str(nieuw)}

        log_actie(
            self.request,
            AuditLog.Actie.BIJGEWERKT,
            instance=instance,
            wijzigingen=wijzigingen,
        )
        return instance

    def perform_destroy(self, instance):
        log_actie(
            self.request,
            AuditLog.Actie.VERWIJDERD,
            instance=instance,
        )
        instance.delete()
