"""Modellen voor standaarden en de koppeling met pakketten."""
from django.db import models

from apps.core.models import BaseModel


class Standaard(BaseModel):
    """Een standaard van het Forum Standaardisatie."""

    class Type(models.TextChoices):
        VERPLICHT = "verplicht", "Verplicht (pas toe of leg uit)"
        AANBEVOLEN = "aanbevolen", "Aanbevolen"
        OPTIONEEL = "optioneel", "Optioneel"

    naam = models.CharField(max_length=255, verbose_name="Naam")
    type = models.CharField(max_length=15, choices=Type.choices, verbose_name="Type")
    versie = models.CharField(max_length=50, blank=True, verbose_name="Versie")
    beschrijving = models.TextField(blank=True, verbose_name="Beschrijving")
    forum_standaardisatie_url = models.URLField(blank=True, verbose_name="Forum Standaardisatie URL")

    class Meta:
        verbose_name = "Standaard"
        verbose_name_plural = "Standaarden"
        ordering = ["naam"]

    def __str__(self):
        return f"{self.naam} ({self.get_type_display()})"


class PakketStandaard(BaseModel):
    """Many-to-many relatie tussen Pakket en Standaard met extra velden."""

    pakket = models.ForeignKey(
        "pakketten.Pakket", on_delete=models.CASCADE, related_name="pakket_standaarden", verbose_name="Pakket"
    )
    standaard = models.ForeignKey(
        Standaard, on_delete=models.CASCADE, related_name="pakket_standaarden", verbose_name="Standaard"
    )
    ondersteund = models.BooleanField(default=True, verbose_name="Ondersteund")
    testrapport_url = models.URLField(blank=True, verbose_name="Testrapport URL")

    class Meta:
        verbose_name = "Pakket-standaard"
        verbose_name_plural = "Pakket-standaarden"
        unique_together = ["pakket", "standaard"]

    def __str__(self):
        status = "✓" if self.ondersteund else "✗"
        return f"{self.pakket.naam} — {self.standaard.naam} [{status}]"
