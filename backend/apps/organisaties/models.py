"""Modellen voor organisaties (gemeenten, leveranciers, samenwerkingsverbanden)."""
from django.db import models

from apps.core.models import BaseModel


class Organisatie(BaseModel):
    """Een organisatie die software aanbiedt of gebruikt."""

    class Type(models.TextChoices):
        GEMEENTE = "gemeente", "Gemeente"
        SAMENWERKINGSVERBAND = "samenwerkingsverband", "Samenwerkingsverband"
        LEVERANCIER = "leverancier", "Leverancier"
        OVERIG = "overig", "Overig"

    class Status(models.TextChoices):
        CONCEPT = "concept", "Concept"
        ACTIEF = "actief", "Actief"
        INACTIEF = "inactief", "Inactief"

    naam = models.CharField(max_length=255, verbose_name="Naam")
    type = models.CharField(max_length=25, choices=Type.choices, verbose_name="Type organisatie")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CONCEPT, verbose_name="Status")
    oin = models.CharField(max_length=20, blank=True, verbose_name="Organisatie Identificatienummer (OIN)")
    bevoegd_gezag_code = models.CharField(max_length=10, blank=True, verbose_name="Bevoegd gezag code")
    website = models.URLField(blank=True, verbose_name="Website")
    beschrijving = models.TextField(blank=True, verbose_name="Beschrijving")
    geregistreerd_door = models.ForeignKey(
        "gebruikers.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="geregistreerde_organisaties",
        verbose_name="Geregistreerd door",
    )
    legacy_id = models.CharField(max_length=100, blank=True, db_index=True, verbose_name="Legacy ID (migratie)")

    class Meta:
        verbose_name = "Organisatie"
        verbose_name_plural = "Organisaties"
        ordering = ["naam"]

    def __str__(self):
        return f"{self.naam} ({self.get_type_display()})"


class Contactpersoon(BaseModel):
    """Contactpersoon van een organisatie."""

    organisatie = models.ForeignKey(
        Organisatie,
        on_delete=models.CASCADE,
        related_name="contactpersonen",
        verbose_name="Organisatie",
    )
    naam = models.CharField(max_length=255, verbose_name="Naam")
    email = models.EmailField(verbose_name="E-mailadres")
    telefoon = models.CharField(max_length=20, blank=True, verbose_name="Telefoonnummer")
    functie = models.CharField(max_length=255, blank=True, verbose_name="Functie")

    class Meta:
        verbose_name = "Contactpersoon"
        verbose_name_plural = "Contactpersonen"

    def __str__(self):
        return f"{self.naam} ({self.organisatie.naam})"
