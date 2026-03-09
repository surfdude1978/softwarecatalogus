"""Gedeelde basismodellen voor de Softwarecatalogus."""

import uuid

from django.db import models


class BaseModel(models.Model):
    """Abstract basismodel met UUID, timestamps en soft delete."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    aangemaakt_op = models.DateTimeField(auto_now_add=True, verbose_name="Aangemaakt op")
    gewijzigd_op = models.DateTimeField(auto_now=True, verbose_name="Gewijzigd op")

    class Meta:
        abstract = True
        ordering = ["-aangemaakt_op"]
