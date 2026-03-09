"""Serializers voor organisaties."""
from rest_framework import serializers

from .models import Contactpersoon, Organisatie


class ContactpersoonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contactpersoon
        fields = ["id", "naam", "email", "telefoon", "functie"]
        read_only_fields = ["id"]


class OrganisatieListSerializer(serializers.ModelSerializer):
    """Compacte weergave voor lijsten."""
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Organisatie
        fields = ["id", "naam", "type", "type_display", "status", "website"]


class OrganisatieDetailSerializer(serializers.ModelSerializer):
    """Volledige weergave voor detailpagina."""
    contactpersonen = ContactpersoonSerializer(many=True, read_only=True)
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    aantal_pakketten = serializers.SerializerMethodField()

    class Meta:
        model = Organisatie
        fields = [
            "id", "naam", "type", "type_display", "status", "status_display",
            "oin", "bevoegd_gezag_code", "website", "beschrijving",
            "contactpersonen", "aantal_pakketten",
            "aangemaakt_op", "gewijzigd_op",
        ]
        read_only_fields = ["id", "aangemaakt_op", "gewijzigd_op"]

    def get_aantal_pakketten(self, obj):
        if obj.type == Organisatie.Type.LEVERANCIER:
            return obj.pakketten.filter(status="actief").count()
        return obj.pakketgebruik.filter(status="in_gebruik").count()


class OrganisatieCreateSerializer(serializers.ModelSerializer):
    """Serializer voor het aanmaken van organisaties."""
    class Meta:
        model = Organisatie
        fields = [
            "id", "naam", "type", "oin", "bevoegd_gezag_code",
            "website", "beschrijving",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        user = self.context["request"].user
        # Zelfregistratie kan anoniem zijn; in dat geval blijft geregistreerd_door None
        if user and user.is_authenticated:
            validated_data["geregistreerd_door"] = user
        validated_data["status"] = Organisatie.Status.CONCEPT
        return super().create(validated_data)
