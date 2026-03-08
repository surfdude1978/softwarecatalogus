"""Serializers voor standaarden."""
from rest_framework import serializers

from .models import PakketStandaard, Standaard


class StandaardSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Standaard
        fields = [
            "id", "naam", "type", "type_display", "versie",
            "beschrijving", "forum_standaardisatie_url",
        ]
        read_only_fields = ["id"]


class PakketStandaardSerializer(serializers.ModelSerializer):
    standaard_naam = serializers.CharField(source="standaard.naam", read_only=True)

    class Meta:
        model = PakketStandaard
        fields = [
            "id", "pakket", "standaard", "standaard_naam",
            "ondersteund", "testrapport_url",
        ]
        read_only_fields = ["id"]
