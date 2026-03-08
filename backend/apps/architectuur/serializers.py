"""Serializers voor GEMMA architectuur."""
from rest_framework import serializers

from .models import GemmaComponent, PakketGemmaComponent


class GemmaComponentListSerializer(serializers.ModelSerializer):
    """Compacte weergave voor lijsten en geneste relaties."""
    class Meta:
        model = GemmaComponent
        fields = ["id", "naam", "archimate_id", "type"]


class GemmaComponentDetailSerializer(serializers.ModelSerializer):
    """Volledige weergave met children en gekoppelde pakketten."""
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    parent_naam = serializers.CharField(source="parent.naam", read_only=True, default=None)
    children = GemmaComponentListSerializer(many=True, read_only=True)
    pakketten = serializers.SerializerMethodField()

    class Meta:
        model = GemmaComponent
        fields = [
            "id", "naam", "archimate_id", "type", "type_display",
            "beschrijving", "gemma_online_url",
            "parent", "parent_naam", "children", "pakketten",
        ]

    def get_pakketten(self, obj):
        from apps.pakketten.models import Pakket
        pakketten = obj.pakketten.filter(status=Pakket.Status.ACTIEF)[:20]
        return [{"id": str(p.id), "naam": p.naam} for p in pakketten]


class PakketGemmaComponentSerializer(serializers.ModelSerializer):
    gemma_component_naam = serializers.CharField(source="gemma_component.naam", read_only=True)

    class Meta:
        model = PakketGemmaComponent
        fields = ["id", "pakket", "gemma_component", "gemma_component_naam"]
        read_only_fields = ["id"]
