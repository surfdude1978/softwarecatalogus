"""Serializers voor documenten."""

from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    gedeeld_met_display = serializers.CharField(source="get_gedeeld_met_display", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "pakket",
            "organisatie",
            "type",
            "type_display",
            "naam",
            "bestand",
            "status",
            "status_display",
            "gedeeld_met",
            "gedeeld_met_display",
            "aangemaakt_op",
        ]
        read_only_fields = ["id", "aangemaakt_op"]
