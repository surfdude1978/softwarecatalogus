"""Modellen voor softwarepakketten, gebruik en koppelingen."""

from django.db import models

from apps.core.models import BaseModel


class Pakket(BaseModel):
    """Een softwarepakket/voorziening in de catalogus."""

    class Status(models.TextChoices):
        CONCEPT = "concept", "Concept"
        ACTIEF = "actief", "Actief"
        VEROUDERD = "verouderd", "Verouderd"
        INGETROKKEN = "ingetrokken", "Ingetrokken"

    class Licentievorm(models.TextChoices):
        COMMERCIEEL = "commercieel", "Commercieel"
        OPEN_SOURCE = "open_source", "Open source"
        SAAS = "saas", "SaaS"
        ANDERS = "anders", "Anders"

    naam = models.CharField(max_length=255, verbose_name="Naam")
    versie = models.CharField(max_length=50, blank=True, verbose_name="Versie")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.CONCEPT, verbose_name="Status")
    beschrijving = models.TextField(blank=True, verbose_name="Beschrijving")
    leverancier = models.ForeignKey(
        "organisaties.Organisatie",
        on_delete=models.CASCADE,
        related_name="pakketten",
        verbose_name="Leverancier",
    )
    licentievorm = models.CharField(
        max_length=15, choices=Licentievorm.choices, default=Licentievorm.COMMERCIEEL, verbose_name="Licentievorm"
    )
    open_source_licentie = models.CharField(
        max_length=50, blank=True, verbose_name="Open source licentie", help_text="Bijv. EUPL, MIT, GPL"
    )
    website_url = models.URLField(blank=True, verbose_name="Website")
    documentatie_url = models.URLField(blank=True, verbose_name="Documentatie URL")
    cloud_provider = models.CharField(max_length=100, blank=True, verbose_name="Cloud provider")
    contactpersoon = models.CharField(max_length=255, blank=True, verbose_name="Contactpersoon")
    geregistreerd_door = models.ForeignKey(
        "gebruikers.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="geregistreerde_pakketten",
        verbose_name="Geregistreerd door",
    )
    gemma_componenten = models.ManyToManyField(
        "architectuur.GemmaComponent",
        through="architectuur.PakketGemmaComponent",
        blank=True,
        related_name="pakketten",
        verbose_name="GEMMA componenten",
    )
    standaarden = models.ManyToManyField(
        "standaarden.Standaard",
        through="standaarden.PakketStandaard",
        blank=True,
        related_name="pakketten",
        verbose_name="Standaarden",
    )
    legacy_id = models.CharField(max_length=100, blank=True, db_index=True, verbose_name="Legacy ID (migratie)")

    class Meta:
        verbose_name = "Pakket"
        verbose_name_plural = "Pakketten"
        ordering = ["naam"]

    def __str__(self):
        version_str = f" v{self.versie}" if self.versie else ""
        return f"{self.naam}{version_str}"

    @property
    def aantal_gebruikers(self):
        """Aantal organisaties dat dit pakket gebruikt."""
        if hasattr(self, "_aantal_gebruikers_cache"):
            return self._aantal_gebruikers_cache
        return self.pakketgebruik_set.filter(status="in_gebruik").count()

    @aantal_gebruikers.setter
    def aantal_gebruikers(self, value):
        self._aantal_gebruikers_cache = value


class PakketGebruik(BaseModel):
    """Registratie van pakketgebruik door een organisatie."""

    class Status(models.TextChoices):
        IN_GEBRUIK = "in_gebruik", "In gebruik"
        GEPLAND = "gepland", "Gepland"
        GESTOPT = "gestopt", "Gestopt"

    pakket = models.ForeignKey(Pakket, on_delete=models.CASCADE, verbose_name="Pakket")
    organisatie = models.ForeignKey(
        "organisaties.Organisatie",
        on_delete=models.CASCADE,
        related_name="pakketgebruik",
        verbose_name="Organisatie",
    )
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.IN_GEBRUIK, verbose_name="Status")
    start_datum = models.DateField(null=True, blank=True, verbose_name="Startdatum")
    eind_datum = models.DateField(null=True, blank=True, verbose_name="Einddatum")
    notitie = models.TextField(blank=True, verbose_name="Notitie")

    class Meta:
        verbose_name = "Pakketgebruik"
        verbose_name_plural = "Pakketgebruik"
        unique_together = ["pakket", "organisatie"]
        ordering = ["-aangemaakt_op"]

    def __str__(self):
        return f"{self.organisatie.naam} → {self.pakket.naam}"


class Koppeling(BaseModel):
    """Koppeling tussen twee pakketgebruik-registraties."""

    class Type(models.TextChoices):
        API = "api", "API"
        BESTAND = "bestand", "Bestandsuitwisseling"
        DATABASE = "database", "Database"
        MESSAGE_QUEUE = "message_queue", "Message Queue"
        ANDERS = "anders", "Anders"

    van_pakket_gebruik = models.ForeignKey(
        PakketGebruik,
        on_delete=models.CASCADE,
        related_name="koppelingen_van",
        verbose_name="Van pakketgebruik",
    )
    naar_pakket_gebruik = models.ForeignKey(
        PakketGebruik,
        on_delete=models.CASCADE,
        related_name="koppelingen_naar",
        verbose_name="Naar pakketgebruik",
    )
    type = models.CharField(max_length=15, choices=Type.choices, default=Type.API, verbose_name="Type koppeling")
    beschrijving = models.TextField(blank=True, verbose_name="Beschrijving")

    class Meta:
        verbose_name = "Koppeling"
        verbose_name_plural = "Koppelingen"

    def __str__(self):
        return f"{self.van_pakket_gebruik} ↔ {self.naar_pakket_gebruik}"
