"""API ViewSets voor de Softwarecatalogus."""
from django.db.models import Count, Q
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.organisaties.models import Organisatie, Contactpersoon
from apps.organisaties.serializers import (
    OrganisatieListSerializer,
    OrganisatieDetailSerializer,
    OrganisatieCreateSerializer,
    ContactpersoonSerializer,
)
from apps.pakketten.models import Pakket, PakketGebruik, Koppeling
from apps.pakketten.serializers import (
    PakketListSerializer,
    PakketDetailSerializer,
    PakketCreateUpdateSerializer,
    PakketGebruikSerializer,
    KoppelingSerializer,
)
from apps.standaarden.models import Standaard
from apps.standaarden.serializers import StandaardSerializer
from apps.architectuur.models import GemmaComponent
from apps.architectuur.serializers import (
    GemmaComponentListSerializer,
    GemmaComponentDetailSerializer,
)
from apps.documenten.models import Document
from apps.documenten.serializers import DocumentSerializer
from apps.content.models import Nieuwsbericht, Pagina
from apps.content.serializers import (
    NieuwsberichtListSerializer,
    NieuwsberichtDetailSerializer,
    PaginaSerializer,
)
from apps.gebruikers.models import Notificatie
from apps.gebruikers.serializers import (
    UserProfileSerializer,
    NotificatieSerializer,
)

from .permissions import IsAanbodBeheerder, IsGebruikBeheerder, IsFunctioneelBeheerder


# ====================
# Publieke endpoints
# ====================

class PakketViewSet(viewsets.ModelViewSet):
    """
    Pakketten in de softwarecatalogus.

    list: Lijst van pakketten met zoek- en filtermogelijkheden.
    retrieve: Details van een specifiek pakket.
    create: Nieuw pakket registreren (aanbod-beheerder).
    update: Pakket bijwerken (aanbod-beheerder).
    """
    queryset = Pakket.objects.select_related("leverancier").annotate(
        aantal_gebruikers=Count(
            "pakketgebruik",
            filter=Q(pakketgebruik__status="in_gebruik"),
        )
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "status": ["exact"],
        "licentievorm": ["exact"],
        "leverancier": ["exact"],
        "leverancier__type": ["exact"],
        "gemma_componenten": ["exact"],
        "standaarden": ["exact"],
    }
    search_fields = ["naam", "beschrijving", "leverancier__naam"]
    ordering_fields = ["naam", "aangemaakt_op", "gewijzigd_op", "aantal_gebruikers"]
    ordering = ["naam"]

    def get_serializer_class(self):
        if self.action == "list":
            return PakketListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return PakketCreateUpdateSerializer
        return PakketDetailSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAanbodBeheerder()]
        return [AllowAny()]

    def get_queryset(self):
        qs = super().get_queryset()
        # Publieke gebruikers zien alleen actieve en concept-pakketten
        if not self.request.user.is_authenticated or self.request.user.rol == "publiek":
            qs = qs.filter(status__in=["actief", "concept"])
        return qs


class OrganisatieViewSet(viewsets.ModelViewSet):
    """
    Organisaties (gemeenten, leveranciers, samenwerkingsverbanden).
    """
    queryset = Organisatie.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {"type": ["exact"], "status": ["exact"]}
    search_fields = ["naam", "oin"]
    ordering_fields = ["naam", "aangemaakt_op"]
    ordering = ["naam"]

    def get_serializer_class(self):
        if self.action == "list":
            return OrganisatieListSerializer
        if self.action in ["create"]:
            return OrganisatieCreateSerializer
        return OrganisatieDetailSerializer

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsFunctioneelBeheerder()]
        return [AllowAny()]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            qs = qs.filter(status="actief")
        return qs


class StandaardViewSet(viewsets.ReadOnlyModelViewSet):
    """Standaarden van het Forum Standaardisatie."""
    queryset = Standaard.objects.all()
    serializer_class = StandaardSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {"type": ["exact"]}
    search_fields = ["naam"]
    ordering = ["naam"]


class GemmaComponentViewSet(viewsets.ReadOnlyModelViewSet):
    """GEMMA referentiecomponenten."""
    queryset = GemmaComponent.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {"type": ["exact"], "parent": ["exact", "isnull"]}
    search_fields = ["naam", "archimate_id"]
    ordering = ["naam"]

    def get_serializer_class(self):
        if self.action == "list":
            return GemmaComponentListSerializer
        return GemmaComponentDetailSerializer


class NieuwsberichtViewSet(viewsets.ReadOnlyModelViewSet):
    """Nieuwsberichten."""
    queryset = Nieuwsbericht.objects.filter(gepubliceerd=True)
    permission_classes = [AllowAny]
    ordering = ["-publicatie_datum"]

    def get_serializer_class(self):
        if self.action == "list":
            return NieuwsberichtListSerializer
        return NieuwsberichtDetailSerializer


class PaginaViewSet(viewsets.ReadOnlyModelViewSet):
    """CMS pagina's."""
    queryset = Pagina.objects.filter(gepubliceerd=True)
    serializer_class = PaginaSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"


# ====================
# Beveiligde endpoints
# ====================

class MijnPakketOverzichtViewSet(viewsets.ModelViewSet):
    """
    Pakketoverzicht van de eigen organisatie.

    Gebruik-beheerders beheren hier hun pakketlandschap.
    """
    serializer_class = PakketGebruikSerializer
    permission_classes = [IsGebruikBeheerder]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {"status": ["exact"], "pakket": ["exact"]}
    ordering = ["-aangemaakt_op"]

    def get_queryset(self):
        user = self.request.user
        if user.rol == "functioneel_beheerder":
            return PakketGebruik.objects.select_related("pakket", "organisatie").all()
        if user.organisatie:
            return PakketGebruik.objects.select_related("pakket", "organisatie").filter(
                organisatie=user.organisatie
            )
        return PakketGebruik.objects.none()


class GemeentePakketOverzichtViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Pakketoverzicht van een andere gemeente bekijken ('gluren bij de buren').
    """
    serializer_class = PakketGebruikSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        gemeente_id = self.kwargs.get("gemeente_id")
        return PakketGebruik.objects.select_related("pakket", "organisatie").filter(
            organisatie_id=gemeente_id,
            status="in_gebruik",
        )


class KoppelingViewSet(viewsets.ModelViewSet):
    """Koppelingen tussen pakketten in eigen landschap."""
    serializer_class = KoppelingSerializer
    permission_classes = [IsGebruikBeheerder]

    def get_queryset(self):
        user = self.request.user
        if user.organisatie:
            return Koppeling.objects.filter(
                Q(van_pakket_gebruik__organisatie=user.organisatie)
                | Q(naar_pakket_gebruik__organisatie=user.organisatie)
            )
        return Koppeling.objects.none()


class DocumentViewSet(viewsets.ModelViewSet):
    """Documenten (DPIA's, verwerkersovereenkomsten, etc.)."""
    serializer_class = DocumentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {"type": ["exact"], "pakket": ["exact"], "status": ["exact"]}

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAanbodBeheerder()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        user = self.request.user
        qs = Document.objects.select_related("pakket", "organisatie")

        if not user.is_authenticated:
            return qs.filter(status="gepubliceerd", gedeeld_met="publiek")

        if user.rol == "functioneel_beheerder":
            return qs

        # Gemeentegebruikers zien publieke + gemeenten-documenten
        filters = Q(status="gepubliceerd") & (
            Q(gedeeld_met="publiek") | Q(gedeeld_met="gemeenten")
        )
        # Plus eigen prive documenten
        if user.organisatie:
            filters |= Q(organisatie=user.organisatie)

        return qs.filter(filters)


class ProfielViewSet(viewsets.GenericViewSet):
    """Eigen gebruikersprofiel."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get", "put", "patch"])
    def mij(self, request):
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class NotificatieViewSet(viewsets.ReadOnlyModelViewSet):
    """Notificaties voor de ingelogde gebruiker."""
    serializer_class = NotificatieSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notificatie.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def markeer_gelezen(self, request, pk=None):
        notificatie = self.get_object()
        notificatie.gelezen = True
        notificatie.save(update_fields=["gelezen"])
        return Response({"status": "gelezen"})

    @action(detail=False, methods=["post"])
    def markeer_alles_gelezen(self, request):
        self.get_queryset().filter(gelezen=False).update(gelezen=True)
        return Response({"status": "alles gelezen"})


# ====================
# Admin endpoints
# ====================

class AdminOrganisatieViewSet(viewsets.ModelViewSet):
    """Admin beheer van organisaties (functioneel beheerder)."""
    queryset = Organisatie.objects.all()
    serializer_class = OrganisatieDetailSerializer
    permission_classes = [IsFunctioneelBeheerder]

    @action(detail=False, methods=["get"])
    def concept(self, request):
        """Lijst van organisaties die wachten op fiattering."""
        concepten = Organisatie.objects.filter(status="concept")
        serializer = OrganisatieListSerializer(concepten, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def fiatteren(self, request, pk=None):
        """Fiattering van een concept-organisatie."""
        organisatie = self.get_object()
        if organisatie.status != "concept":
            return Response(
                {"detail": "Alleen concept-organisaties kunnen worden gefiatteerd."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        organisatie.status = Organisatie.Status.ACTIEF
        organisatie.save(update_fields=["status", "gewijzigd_op"])
        return Response(OrganisatieDetailSerializer(organisatie).data)

    @action(detail=False, methods=["post"])
    def samenvoegen(self, request):
        """Twee organisaties samenvoegen (bij herindeling)."""
        bron_id = request.data.get("bron_id")
        doel_id = request.data.get("doel_id")
        if not bron_id or not doel_id:
            return Response(
                {"detail": "bron_id en doel_id zijn verplicht."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            bron = Organisatie.objects.get(pk=bron_id)
            doel = Organisatie.objects.get(pk=doel_id)
        except Organisatie.DoesNotExist:
            return Response(
                {"detail": "Organisatie niet gevonden."},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Verplaats gerelateerde objecten
        bron.gebruikers.update(organisatie=doel)
        bron.pakketgebruik.update(organisatie=doel)
        bron.contactpersonen.update(organisatie=doel)
        if bron.type == Organisatie.Type.LEVERANCIER:
            bron.pakketten.update(leverancier=doel)
        bron.status = Organisatie.Status.INACTIEF
        bron.save(update_fields=["status", "gewijzigd_op"])
        return Response({"detail": f"{bron.naam} samengevoegd met {doel.naam}."})
