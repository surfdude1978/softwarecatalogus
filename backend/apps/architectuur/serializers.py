"""Serializers voor GEMMA architectuur."""

from rest_framework import serializers

from .models import GemmaComponent, PakketGemmaComponent


class GemmaKaartComponentSerializer(serializers.ModelSerializer):
    """Recursieve serializer voor de GEMMA architectuurkaart.

    Geeft de volledige componenthiërarchie terug met, per component:
    - kinderen (recursief, max. 3 niveaus diep)
    - pakketten gekoppeld aan dit component
      · voor geauthenticeerde gebruikers: alleen eigen pakketgebruik
      · voor anonieme gebruikers: actieve pakketten (max. 5 per component)
    """

    kinderen = serializers.SerializerMethodField()
    pakketten = serializers.SerializerMethodField()
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = GemmaComponent
        fields = [
            "id",
            "naam",
            "archimate_id",
            "type",
            "type_display",
            "beschrijving",
            "gemma_online_url",
            "kinderen",
            "pakketten",
        ]

    def get_kinderen(self, obj):
        niveau = self.context.get("_niveau", 0)
        if niveau >= 3:
            return []
        kinderen = obj.children.all().order_by("naam")
        ctx = {**self.context, "_niveau": niveau + 1}
        return GemmaKaartComponentSerializer(kinderen, many=True, context=ctx).data

    def get_pakketten(self, obj):
        from apps.pakketten.models import Pakket, PakketGebruik

        request = self.context.get("request")
        if request and request.user.is_authenticated and getattr(request.user, "organisatie", None):
            # Geauthenticeerde gebruiker: toon eigen pakketgebruik
            pg_qs = PakketGebruik.objects.filter(
                pakket__gemma_componenten=obj,
                organisatie=request.user.organisatie,
            ).select_related("pakket", "pakket__leverancier")
            return [
                {
                    "id": str(pg.pakket.id),
                    "naam": pg.pakket.naam,
                    "leverancier_naam": (pg.pakket.leverancier.naam if pg.pakket.leverancier else ""),
                    "status_gebruik": pg.status,
                    "licentievorm": pg.pakket.licentievorm or "",
                }
                for pg in pg_qs
            ]
        # Anoniem: actieve pakketten, max 5
        pakketten = obj.pakketten.filter(status=Pakket.Status.ACTIEF).select_related("leverancier")[:5]
        return [
            {
                "id": str(p.id),
                "naam": p.naam,
                "leverancier_naam": p.leverancier.naam if p.leverancier else "",
                "status_gebruik": None,
                "licentievorm": p.licentievorm or "",
            }
            for p in pakketten
        ]


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
            "id",
            "naam",
            "archimate_id",
            "type",
            "type_display",
            "beschrijving",
            "gemma_online_url",
            "parent",
            "parent_naam",
            "children",
            "pakketten",
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
