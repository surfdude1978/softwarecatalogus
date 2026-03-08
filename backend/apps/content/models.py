"""Modellen voor CMS-content (nieuwsberichten, teksten)."""
from django.db import models

from apps.core.models import BaseModel


class Pagina(BaseModel):
    """Een CMS-pagina met configureerbare content."""

    titel = models.CharField(max_length=255, verbose_name="Titel")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug")
    inhoud = models.TextField(verbose_name="Inhoud")
    gepubliceerd = models.BooleanField(default=False, verbose_name="Gepubliceerd")
    auteur = models.ForeignKey(
        "gebruikers.User", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Auteur"
    )

    class Meta:
        verbose_name = "Pagina"
        verbose_name_plural = "Pagina's"
        ordering = ["-aangemaakt_op"]

    def __str__(self):
        return self.titel


class Nieuwsbericht(BaseModel):
    """Een nieuwsbericht op de softwarecatalogus."""

    titel = models.CharField(max_length=255, verbose_name="Titel")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug")
    samenvatting = models.TextField(max_length=500, verbose_name="Samenvatting")
    inhoud = models.TextField(verbose_name="Inhoud")
    afbeelding = models.ImageField(upload_to="nieuws/", blank=True, verbose_name="Afbeelding")
    gepubliceerd = models.BooleanField(default=False, verbose_name="Gepubliceerd")
    publicatie_datum = models.DateTimeField(null=True, blank=True, verbose_name="Publicatiedatum")
    auteur = models.ForeignKey(
        "gebruikers.User", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Auteur"
    )

    class Meta:
        verbose_name = "Nieuwsbericht"
        verbose_name_plural = "Nieuwsberichten"
        ordering = ["-publicatie_datum"]

    def __str__(self):
        return self.titel
