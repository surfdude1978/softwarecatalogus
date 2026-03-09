"""Serializers voor TenderNed aanbestedingen."""

from rest_framework import serializers

from apps.architectuur.serializers import GemmaComponentListSerializer
from apps.organisaties.serializers import OrganisatieListSerializer

from .models import Aanbesteding


class AanbestedingenListSerializer(serializers.ModelSerializer):
    """Compacte serializer voor aanbestedingen-overzicht en widget."""

    gemma_component_namen = serializers.SerializerMethodField()
    primaire_cpv = serializers.ReadOnlyField()
    aanbestedende_dienst_naam = serializers.CharField(source="aanbestedende_dienst", read_only=True)

    class Meta:
        model = Aanbesteding
        fields = [
            "id",
            "publicatiecode",
            "naam",
            "aanbestedende_dienst",
            "aanbestedende_dienst_naam",
            "aanbestedende_dienst_stad",
            "type",
            "status",
            "publicatiedatum",
            "sluitingsdatum",
            "primaire_cpv",
            "cpv_omschrijvingen",
            "waarde_geschat",
            "url_tenderned",
            "gemma_component_namen",
        ]

    def get_gemma_component_namen(self, obj) -> list[str]:
        return list(obj.gemma_componenten.values_list("naam", flat=True))


class AanbestedingenDetailSerializer(serializers.ModelSerializer):
    """Uitgebreide serializer voor aanbesteding-detailpagina."""

    gemma_componenten = GemmaComponentListSerializer(many=True, read_only=True)
    organisatie = OrganisatieListSerializer(read_only=True)
    relevante_pakketten = serializers.SerializerMethodField()
    primaire_cpv = serializers.ReadOnlyField()
    is_ict_aanbesteding = serializers.ReadOnlyField()

    class Meta:
        model = Aanbesteding
        fields = [
            "id",
            "publicatiecode",
            "naam",
            "aanbestedende_dienst",
            "aanbestedende_dienst_stad",
            "type",
            "status",
            "procedure",
            "publicatiedatum",
            "sluitingsdatum",
            "cpv_codes",
            "cpv_omschrijvingen",
            "primaire_cpv",
            "waarde_geschat",
            "url_tenderned",
            "omschrijving",
            "organisatie",
            "gemma_componenten",
            "relevante_pakketten",
            "is_ict_aanbesteding",
            "laatste_sync",
            "aangemaakt_op",
        ]

    def get_relevante_pakketten(self, obj) -> list[dict]:
        return [
            {"id": str(p.id), "naam": p.naam, "leverancier": p.leverancier.naam}
            for p in obj.relevante_pakketten.select_related("leverancier").all()
        ]
