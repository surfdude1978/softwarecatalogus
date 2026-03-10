"""Serializers voor pakketten, gebruik en koppelingen."""

from rest_framework import serializers

from apps.architectuur.serializers import GemmaComponentListSerializer
from apps.organisaties.models import Organisatie
from apps.organisaties.serializers import OrganisatieListSerializer
from apps.standaarden.serializers import StandaardSerializer

from .models import Koppeling, Pakket, PakketGebruik


class PakketListSerializer(serializers.ModelSerializer):
    """Compacte weergave voor zoekresultaten en lijsten."""

    leverancier_naam = serializers.CharField(source="leverancier.naam", read_only=True)
    licentievorm_display = serializers.CharField(source="get_licentievorm_display", read_only=True)
    aantal_gebruikers = serializers.IntegerField(read_only=True)

    class Meta:
        model = Pakket
        fields = [
            "id",
            "naam",
            "versie",
            "status",
            "beschrijving",
            "leverancier",
            "leverancier_naam",
            "licentievorm",
            "licentievorm_display",
            "aantal_gebruikers",
        ]


class PakketDetailSerializer(serializers.ModelSerializer):
    """Volledige weergave voor detailpagina."""

    leverancier = OrganisatieListSerializer(read_only=True)
    licentievorm_display = serializers.CharField(source="get_licentievorm_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    standaarden = StandaardSerializer(many=True, read_only=True)
    gemma_componenten = GemmaComponentListSerializer(many=True, read_only=True)
    aantal_gebruikers = serializers.IntegerField(read_only=True)
    gebruikende_organisaties = serializers.SerializerMethodField()

    class Meta:
        model = Pakket
        fields = [
            "id",
            "naam",
            "versie",
            "status",
            "status_display",
            "beschrijving",
            "leverancier",
            "licentievorm",
            "licentievorm_display",
            "open_source_licentie",
            "website_url",
            "documentatie_url",
            "cloud_provider",
            "contactpersoon",
            "standaarden",
            "gemma_componenten",
            "aantal_gebruikers",
            "gebruikende_organisaties",
            "aangemaakt_op",
            "gewijzigd_op",
        ]
        read_only_fields = ["id", "aangemaakt_op", "gewijzigd_op"]

    def get_gebruikende_organisaties(self, obj):
        gebruik = obj.pakketgebruik_set.filter(status="in_gebruik").select_related("organisatie")[:20]
        return [{"id": str(g.organisatie.id), "naam": g.organisatie.naam} for g in gebruik]


class PakketCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer voor aanmaken/bewerken van pakketten."""

    # leverancier is optioneel in de payload: als niet meegegeven wordt automatisch
    # de organisatie van de ingelogde gebruiker gebruikt (aanbod-beheerder maakt
    # altijd een pakket namens zijn eigen organisatie).
    leverancier = serializers.PrimaryKeyRelatedField(
        queryset=Organisatie.objects.all(),
        required=False,
    )

    class Meta:
        model = Pakket
        fields = [
            "naam",
            "versie",
            "beschrijving",
            "leverancier",
            "licentievorm",
            "open_source_licentie",
            "website_url",
            "documentatie_url",
            "cloud_provider",
            "contactpersoon",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["geregistreerd_door"] = user
        # Gebruik de organisatie van de ingelogde gebruiker als leverancier
        # indien niet expliciet opgegeven in de payload.
        if "leverancier" not in validated_data:
            validated_data["leverancier"] = user.organisatie
        # Pakketten aangemaakt door iemand die niet de leverancier is krijgen concept-status
        if not (user.organisatie and user.organisatie == validated_data.get("leverancier")):
            validated_data["status"] = Pakket.Status.CONCEPT
        return super().create(validated_data)


class PakketGebruikSerializer(serializers.ModelSerializer):
    """Serializer voor pakketgebruik."""

    pakket_naam = serializers.CharField(source="pakket.naam", read_only=True)
    organisatie_naam = serializers.CharField(source="organisatie.naam", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = PakketGebruik
        fields = [
            "id",
            "pakket",
            "pakket_naam",
            "organisatie",
            "organisatie_naam",
            "status",
            "status_display",
            "start_datum",
            "eind_datum",
            "notitie",
            "aangemaakt_op",
            "gewijzigd_op",
        ]
        read_only_fields = ["id", "organisatie", "aangemaakt_op", "gewijzigd_op"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["organisatie"] = user.organisatie
        return super().create(validated_data)


class KoppelingSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Koppeling
        fields = [
            "id",
            "van_pakket_gebruik",
            "naar_pakket_gebruik",
            "type",
            "type_display",
            "beschrijving",
            "aangemaakt_op",
        ]
        read_only_fields = ["id", "aangemaakt_op"]
