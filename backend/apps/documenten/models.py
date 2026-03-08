"""Modellen voor documentbeheer (DPIA's, verwerkersovereenkomsten, etc.)."""
from django.db import models

from apps.core.models import BaseModel


def document_upload_path(instance, filename):
    return f"documenten/{instance.pakket_id}/{filename}"


class Document(BaseModel):
    """Een document gekoppeld aan een pakket."""

    class Type(models.TextChoices):
        DPIA = "dpia", "DPIA"
        VERWERKERSOVEREENKOMST = "verwerkersovereenkomst", "Verwerkersovereenkomst"
        PENTEST = "pentest", "Pentestrapport"
        OVERIG = "overig", "Overig"

    class Status(models.TextChoices):
        CONCEPT = "concept", "Concept"
        GEPUBLICEERD = "gepubliceerd", "Gepubliceerd"

    class Zichtbaarheid(models.TextChoices):
        PUBLIEK = "publiek", "Publiek"
        GEMEENTEN = "gemeenten", "Alleen gemeenten"
        PRIVE = "prive", "Prive"

    pakket = models.ForeignKey(
        "pakketten.Pakket", on_delete=models.CASCADE, related_name="documenten", verbose_name="Pakket"
    )
    organisatie = models.ForeignKey(
        "organisaties.Organisatie",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documenten",
        verbose_name="Organisatie",
    )
    type = models.CharField(max_length=25, choices=Type.choices, verbose_name="Type document")
    naam = models.CharField(max_length=255, verbose_name="Naam")
    bestand = models.FileField(upload_to=document_upload_path, verbose_name="Bestand")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.CONCEPT, verbose_name="Status")
    gedeeld_met = models.CharField(
        max_length=10,
        choices=Zichtbaarheid.choices,
        default=Zichtbaarheid.PRIVE,
        verbose_name="Gedeeld met",
    )

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documenten"
        ordering = ["-aangemaakt_op"]

    def __str__(self):
        return f"{self.naam} ({self.get_type_display()})"
