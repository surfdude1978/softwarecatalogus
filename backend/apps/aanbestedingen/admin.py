"""Django admin configuratie voor TenderNed aanbestedingen."""
from django.contrib import admin
from django.utils.html import format_html

from .models import Aanbesteding


@admin.register(Aanbesteding)
class AanbestedingenAdmin(admin.ModelAdmin):
    list_display = [
        "publicatiecode",
        "naam_kort",
        "aanbestedende_dienst",
        "type",
        "status_badge",
        "publicatiedatum",
        "waarde_geschat",
        "tenderned_link",
    ]
    list_filter = [
        "type",
        "status",
        "publicatiedatum",
    ]
    search_fields = [
        "publicatiecode",
        "naam",
        "aanbestedende_dienst",
    ]
    filter_horizontal = ["gemma_componenten", "relevante_pakketten"]
    autocomplete_fields = ["organisatie"]
    readonly_fields = ["publicatiecode", "laatste_sync", "aangemaakt_op", "gewijzigd_op", "tenderned_link"]
    date_hierarchy = "publicatiedatum"

    fieldsets = [
        ("TenderNed gegevens", {
            "fields": [
                "publicatiecode",
                "naam",
                "aanbestedende_dienst",
                "aanbestedende_dienst_stad",
                "type",
                "status",
                "procedure",
                "publicatiedatum",
                "sluitingsdatum",
                "cpv_codes",
                "cpv_omschrijvingen",
                "waarde_geschat",
                "omschrijving",
                "url_tenderned",
                "tenderned_link",
            ],
        }),
        ("GEMMA-duiding", {
            "fields": ["organisatie", "gemma_componenten", "relevante_pakketten"],
        }),
        ("Metadata", {
            "fields": ["laatste_sync", "aangemaakt_op", "gewijzigd_op"],
            "classes": ["collapse"],
        }),
    ]

    def naam_kort(self, obj):
        return obj.naam[:60] + "…" if len(obj.naam) > 60 else obj.naam
    naam_kort.short_description = "Naam"

    def status_badge(self, obj):
        kleuren = {
            "aankondiging": "#2563eb",
            "gunning": "#16a34a",
            "rectificatie": "#d97706",
            "vooraankondiging": "#7c3aed",
            "onbekend": "#6b7280",
        }
        kleur = kleuren.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background:{};color:white;padding:2px 6px;border-radius:3px;font-size:11px">{}</span>',
            kleur,
            obj.get_status_display(),
        )
    status_badge.short_description = "Type"

    def tenderned_link(self, obj):
        if obj.url_tenderned:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener">Bekijk op TenderNed ↗</a>',
                obj.url_tenderned,
            )
        return "—"
    tenderned_link.short_description = "TenderNed"

    actions = ["herbereken_gemma_koppelingen"]

    @admin.action(description="GEMMA-koppelingen herberekenen")
    def herbereken_gemma_koppelingen(self, request, queryset):
        from apps.aanbestedingen.tasks import _koppel_gemma, _koppel_organisatie

        for aanbesteding in queryset:
            _koppel_organisatie(aanbesteding)
            _koppel_gemma(aanbesteding)

        self.message_user(request, f"{queryset.count()} aanbestedingen bijgewerkt.")
