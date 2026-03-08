"""Modellen voor TenderNed aanbestedingen met GEMMA-duiding."""
from django.db import models

from apps.core.models import BaseModel


class Aanbesteding(BaseModel):
    """
    Een ICT-aanbesteding van TenderNed, verrijkt met GEMMA-duiding.

    Data wordt dagelijks gesynchroniseerd vanuit de TenderNed Open Data API.
    Alleen aanbestedingen met ICT-gerelateerde CPV-codes worden opgeslagen.
    """

    class Type(models.TextChoices):
        EUROPEES = "europees", "Europees"
        NATIONAAL = "nationaal", "Nationaal"
        ONBEKEND = "onbekend", "Onbekend"

    class Status(models.TextChoices):
        AANKONDIGING = "aankondiging", "Aankondiging van opdracht"
        GUNNING = "gunning", "Aankondiging van gegunde opdracht"
        RECTIFICATIE = "rectificatie", "Rectificatie"
        VOORAANKONDIGING = "vooraankondiging", "Vooraankondiging"
        EF25 = "ef25", "EF25 - Vrijwillige ex-post-transparantie"
        ONBEKEND = "onbekend", "Onbekend"

    # ── TenderNed velden ───────────────────────────────────────────────────────
    publicatiecode = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Publicatiecode",
        help_text="Unieke TenderNed publicatiecode (bijv. 2024-545877)",
    )
    naam = models.CharField(max_length=1000, verbose_name="Naam aanbesteding")
    aanbestedende_dienst = models.CharField(
        max_length=500,
        verbose_name="Aanbestedende dienst",
        help_text="Naam van de gemeente of organisatie die aanbesteedt",
    )
    aanbestedende_dienst_stad = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Stad/gemeente",
    )
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.ONBEKEND,
        verbose_name="Type aanbesteding",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AANKONDIGING,
        verbose_name="Type aankondiging",
    )
    procedure = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Procedure",
        help_text="Bijv. Openbare procedure, Niet-openbare procedure",
    )
    publicatiedatum = models.DateField(verbose_name="Publicatiedatum")
    sluitingsdatum = models.DateField(
        null=True, blank=True, verbose_name="Sluitingsdatum"
    )
    cpv_codes = models.JSONField(
        default=list,
        verbose_name="CPV-codes",
        help_text="Lijst van CPV-codes (Common Procurement Vocabulary)",
    )
    cpv_omschrijvingen = models.JSONField(
        default=list,
        verbose_name="CPV-omschrijvingen",
    )
    waarde_geschat = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Geschatte waarde (€)",
    )
    url_tenderned = models.URLField(
        max_length=500,
        verbose_name="URL op TenderNed",
    )
    omschrijving = models.TextField(blank=True, verbose_name="Omschrijving")

    # ── GEMMA-duiding (door ons systeem toegevoegd) ────────────────────────────
    organisatie = models.ForeignKey(
        "organisaties.Organisatie",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="aanbestedingen",
        verbose_name="Gekoppelde organisatie",
        help_text="Gemeente in de Softwarecatalogus die overeenkomt met de aanbestedende dienst",
    )
    gemma_componenten = models.ManyToManyField(
        "architectuur.GemmaComponent",
        blank=True,
        related_name="aanbestedingen",
        verbose_name="GEMMA componenten",
        help_text="GEMMA-componenten die relevant zijn voor deze aanbesteding (afgeleid van CPV-codes)",
    )
    relevante_pakketten = models.ManyToManyField(
        "pakketten.Pakket",
        blank=True,
        related_name="aanbestedingen",
        verbose_name="Relevante pakketten",
        help_text="Pakketten in de catalogus die relevant zijn voor deze aanbesteding",
    )

    # ── Sync metadata ──────────────────────────────────────────────────────────
    laatste_sync = models.DateTimeField(
        auto_now=True,
        verbose_name="Laatste synchronisatie",
    )

    class Meta:
        verbose_name = "Aanbesteding"
        verbose_name_plural = "Aanbestedingen"
        ordering = ["-publicatiedatum"]
        indexes = [
            models.Index(fields=["-publicatiedatum"]),
            models.Index(fields=["aanbestedende_dienst"]),
        ]

    def __str__(self):
        return f"{self.publicatiecode} — {self.naam[:80]}"

    @property
    def primaire_cpv(self):
        """Geef de eerste (primaire) CPV-code terug."""
        return self.cpv_codes[0] if self.cpv_codes else None

    @property
    def is_ict_aanbesteding(self):
        """Controleer of dit een ICT-aanbesteding is op basis van CPV-codes."""
        ict_prefixen = ("48", "72")
        return any(
            str(cpv).startswith(prefix)
            for cpv in self.cpv_codes
            for prefix in ict_prefixen
        )
