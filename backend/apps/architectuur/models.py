"""Modellen voor GEMMA referentiearchitectuur (ArchiMate)."""
from django.db import models

from apps.core.models import BaseModel


class GemmaComponent(BaseModel):
    """Een GEMMA referentiecomponent uit het ArchiMate-model."""

    class Type(models.TextChoices):
        APPLICATIE_COMPONENT = "applicatiecomponent", "Applicatiecomponent"
        APPLICATIE_SERVICE = "applicatieservice", "Applicatieservice"
        APPLICATIE_FUNCTIE = "applicatiefunctie", "Applicatiefunctie"
        ANDERS = "anders", "Anders"

    naam = models.CharField(max_length=255, verbose_name="Naam")
    archimate_id = models.CharField(max_length=100, unique=True, verbose_name="ArchiMate ID")
    type = models.CharField(
        max_length=25, choices=Type.choices, default=Type.APPLICATIE_COMPONENT, verbose_name="Type"
    )
    beschrijving = models.TextField(blank=True, verbose_name="Beschrijving")
    gemma_online_url = models.URLField(blank=True, verbose_name="GEMMA Online URL")
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Bovenliggend component",
    )

    class Meta:
        verbose_name = "GEMMA component"
        verbose_name_plural = "GEMMA componenten"
        ordering = ["naam"]

    def __str__(self):
        return self.naam


class PakketGemmaComponent(BaseModel):
    """Many-to-many relatie tussen Pakket en GemmaComponent."""

    pakket = models.ForeignKey(
        "pakketten.Pakket", on_delete=models.CASCADE, related_name="pakket_gemma", verbose_name="Pakket"
    )
    gemma_component = models.ForeignKey(
        GemmaComponent, on_delete=models.CASCADE, related_name="pakket_gemma", verbose_name="GEMMA component"
    )

    class Meta:
        verbose_name = "Pakket-GEMMA component"
        verbose_name_plural = "Pakket-GEMMA componenten"
        unique_together = ["pakket", "gemma_component"]

    def __str__(self):
        return f"{self.pakket.naam} → {self.gemma_component.naam}"
