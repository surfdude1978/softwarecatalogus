"""Serializers voor CMS content."""
from rest_framework import serializers

from .models import Nieuwsbericht, Pagina


class PaginaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagina
        fields = ["id", "titel", "slug", "inhoud", "gepubliceerd", "aangemaakt_op", "gewijzigd_op"]
        read_only_fields = ["id", "aangemaakt_op", "gewijzigd_op"]


class NieuwsberichtListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nieuwsbericht
        fields = ["id", "titel", "slug", "samenvatting", "afbeelding", "publicatie_datum"]


class NieuwsberichtDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nieuwsbericht
        fields = [
            "id", "titel", "slug", "samenvatting", "inhoud",
            "afbeelding", "gepubliceerd", "publicatie_datum",
            "aangemaakt_op", "gewijzigd_op",
        ]
        read_only_fields = ["id", "aangemaakt_op", "gewijzigd_op"]
