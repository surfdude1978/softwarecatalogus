"""API ViewSets voor de Softwarecatalogus."""
from django.db.models import Count, Q
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from apps.api.permissions import IsFullyAuthenticated  # noqa: E402 – na rest_framework imports
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
from apps.architectuur.models import GemmaComponent, PakketGemmaComponent
from apps.architectuur.serializers import (
    GemmaComponentListSerializer,
    GemmaComponentDetailSerializer,
    GemmaKaartComponentSerializer,
)
from apps.documenten.models import Document
from apps.documenten.serializers import DocumentSerializer
from apps.content.models import Nieuwsbericht, Pagina
from apps.content.serializers import (
    NieuwsberichtListSerializer,
    NieuwsberichtDetailSerializer,
    PaginaSerializer,
)
from apps.gebruikers.models import Notificatie, User
from apps.gebruikers.serializers import (
    UserProfileSerializer,
    NotificatieSerializer,
)

from apps.aanbestedingen.models import Aanbesteding
from apps.aanbestedingen.serializers import (
    AanbestedingenListSerializer,
    AanbestedingenDetailSerializer,
)

from .permissions import IsAanbodBeheerder, IsGebruikBeheerder, IsFunctioneelBeheerder
from apps.core.audit import AuditLogMixin, log_actie, AuditLog


# ====================
# Publieke endpoints
# ====================

class PakketViewSet(AuditLogMixin, viewsets.ModelViewSet):
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
        if self.action in ["create", "update", "partial_update", "destroy", "stel_gemma_in"]:
            return [IsAanbodBeheerder()]
        return [AllowAny()]

    def get_queryset(self):
        qs = super().get_queryset()
        # Publieke gebruikers zien alleen gepubliceerde (actieve) pakketten
        # Concept-pakketten zijn intern en nog niet goedgekeurd
        if not self.request.user.is_authenticated or self.request.user.rol == "publiek":
            qs = qs.filter(status="actief")
        return qs

    @action(detail=True, methods=["get", "put"], url_path="gemma-componenten", url_name="gemma-componenten")
    def stel_gemma_in(self, request, pk=None):
        """
        GET  — huidige GEMMA-componentkoppelingen ophalen.
        PUT  — GEMMA-componentkoppelingen vervangen (volledige lijst meesturen).

        Verwacht bij PUT: { "gemma_component_ids": ["uuid1", "uuid2", ...] }
        """
        pakket = self.get_object()

        if request.method == "GET":
            componenten = pakket.gemma_componenten.all()
            return Response({
                "gemma_component_ids": [str(c.id) for c in componenten],
                "gemma_componenten": GemmaComponentListSerializer(componenten, many=True).data,
            })

        # PUT — vervang alle koppelingen
        component_ids = request.data.get("gemma_component_ids", [])
        if not isinstance(component_ids, list):
            return Response(
                {"detail": "gemma_component_ids moet een lijst zijn."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Valideer dat alle opgegeven IDs bestaan
        componenten = GemmaComponent.objects.filter(id__in=component_ids)
        if len(component_ids) > 0 and componenten.count() != len(component_ids):
            return Response(
                {"detail": "Een of meer GEMMA-component IDs zijn ongeldig."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Vervang alle bestaande koppelingen atomair
        PakketGemmaComponent.objects.filter(pakket=pakket).delete()
        if componenten:
            PakketGemmaComponent.objects.bulk_create([
                PakketGemmaComponent(pakket=pakket, gemma_component=c)
                for c in componenten
            ])

        return Response({
            "gemma_component_ids": [str(c.id) for c in componenten],
            "gemma_componenten": GemmaComponentListSerializer(componenten, many=True).data,
        })


class OrganisatieViewSet(AuditLogMixin, viewsets.ModelViewSet):
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
    pagination_class = None  # Klein, stabiel dataset — geen paginering nodig
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {"type": ["exact"], "parent": ["exact", "isnull"]}
    search_fields = ["naam", "archimate_id"]
    ordering = ["naam"]

    def get_serializer_class(self):
        if self.action == "list":
            return GemmaComponentListSerializer
        return GemmaComponentDetailSerializer


from rest_framework.views import APIView as _APIView  # noqa: E402


class GemmaKaartView(_APIView):
    """
    GEMMA architectuurkaart — volledige componenthiërarchie met pakketten.

    Geeft alle root-componenten terug (parent=null), met recursief geneste
    kinderen (max 3 niveaus) en de bijbehorende pakketten per component.

    Geauthenticeerde gebruikers zien hun eigen pakketgebruik per component.
    Anonieme gebruikers zien maximaal 5 actieve pakketten per component.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        root_componenten = (
            GemmaComponent.objects.filter(parent__isnull=True)
            .prefetch_related(
                "children",
                "children__children",
                "children__children__children",
            )
            .order_by("naam")
        )
        serializer = GemmaKaartComponentSerializer(
            root_componenten,
            many=True,
            context={"request": request, "_niveau": 0},
        )
        return Response({"componenten": serializer.data})


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

class MijnPakketOverzichtViewSet(AuditLogMixin, viewsets.ModelViewSet):
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
    permission_classes = [IsFullyAuthenticated]

    def get_queryset(self):
        gemeente_id = self.kwargs.get("gemeente_id")
        return PakketGebruik.objects.select_related("pakket", "organisatie").filter(
            organisatie_id=gemeente_id,
            status="in_gebruik",
        )


class KoppelingViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """Koppelingen tussen pakketten in eigen landschap."""
    serializer_class = KoppelingSerializer
    permission_classes = [IsGebruikBeheerder]

    def get_queryset(self):
        user = self.request.user
        if user.organisatie:
            return Koppeling.objects.filter(
                Q(van_pakket_gebruik__organisatie=user.organisatie)
                | Q(naar_pakket_gebruik__organisatie=user.organisatie)
            ).order_by("-aangemaakt_op")
        return Koppeling.objects.none()


class DocumentViewSet(AuditLogMixin, viewsets.ModelViewSet):
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
    permission_classes = [IsFullyAuthenticated]

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
    permission_classes = [IsFullyAuthenticated]

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

class AdminOrganisatieViewSet(AuditLogMixin, viewsets.ModelViewSet):
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
        log_actie(
            request,
            AuditLog.Actie.GEFIATEERD,
            instance=organisatie,
            extra={"vorige_status": "concept"},
        )
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


class AdminGebruikerViewSet(AuditLogMixin, viewsets.ReadOnlyModelViewSet):
    """
    Admin beheer van gebruikers (functioneel beheerder).

    list: Alle gebruikers (optioneel gefilterd op ?status=wacht_op_fiattering).
    retrieve: Details van een gebruiker.
    wachtend: Lijst van gebruikers die wachten op fiattering.
    fiatteren: Activeer een wachtende gebruiker.
    """
    queryset = User.objects.select_related("organisatie").all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsFunctioneelBeheerder]
    filter_backends = [filters.SearchFilter]
    search_fields = ["naam", "email", "organisatie__naam"]

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    @action(detail=False, methods=["get"])
    def wachtend(self, request):
        """Lijst van gebruikers die wachten op fiattering."""
        wachtenden = (
            User.objects.filter(status=User.Status.WACHT_OP_FIATTERING)
            .exclude(email="AnonymousUser")  # guardian anonieme gebruiker uitsluiten
            .select_related("organisatie")
            .order_by("aangemaakt_op")
        )
        serializer = UserProfileSerializer(wachtenden, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def fiatteren(self, request, pk=None):
        """Activeer een wachtende gebruiker na handmatige controle."""
        gebruiker = self.get_object()
        if gebruiker.status != User.Status.WACHT_OP_FIATTERING:
            return Response(
                {"detail": "Alleen wachtende gebruikers kunnen worden gefiatteerd."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        gebruiker.status = User.Status.ACTIEF
        gebruiker.save(update_fields=["status"])
        log_actie(
            request,
            AuditLog.Actie.GEFIATEERD,
            instance=gebruiker,
            extra={"vorige_status": "wacht_op_fiattering"},
        )
        # TODO: Stuur welkomstmail via Celery (send_welcome_email.delay(gebruiker.id))
        return Response(UserProfileSerializer(gebruiker).data)

    @action(detail=True, methods=["post"])
    def afwijzen(self, request, pk=None):
        """Wijs een wachtende gebruiker af (status → inactief)."""
        gebruiker = self.get_object()
        if gebruiker.status != User.Status.WACHT_OP_FIATTERING:
            return Response(
                {"detail": "Alleen wachtende gebruikers kunnen worden afgewezen."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reden = request.data.get("reden", "")
        gebruiker.status = User.Status.INACTIEF
        gebruiker.save(update_fields=["status"])
        log_actie(
            request,
            AuditLog.Actie.GEFIATEERD,
            instance=gebruiker,
            extra={"vorige_status": "wacht_op_fiattering", "afgewezen": True, "reden": reden},
        )
        # TODO: Stuur afwijzingsmail via Celery
        return Response({"detail": "Gebruiker afgewezen."})


# ====================
# Aanbestedingen (TenderNed)
# ====================

class AanbestedingenViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ICT-aanbestedingen van Nederlandse gemeenten vanuit TenderNed.

    list: Overzicht van recente ICT-aanbestedingen (publiek, geen auth).
    retrieve: Detail van een aanbesteding.

    Filterparameters:
    - type: europees | nationaal
    - status: aankondiging | gunning | rectificatie | vooraankondiging
    - organisatie: UUID van gekoppelde gemeente
    - publicatiedatum__gte: Datum vanaf (YYYY-MM-DD)
    - publicatiedatum__lte: Datum tot (YYYY-MM-DD)
    - gemeente: naam van gemeente (fuzzy-match op aanbestedende_dienst)
    - pakket: UUID van pakket (filtert via GEMMA-componenten van dat pakket)
    - leverancier: UUID van leverancier (filtert via GEMMA-componenten van hun pakketten)
    - gemma: naam van GEMMA-component (icontains match)
    - cpv: specifieke CPV-code
    """

    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "type": ["exact"],
        "status": ["exact"],
        "organisatie": ["exact"],
        "publicatiedatum": ["gte", "lte", "exact"],
    }
    search_fields = [
        "naam",
        "aanbestedende_dienst",
        "omschrijving",
        "cpv_omschrijvingen",
    ]
    ordering_fields = ["publicatiedatum", "sluitingsdatum", "waarde_geschat", "naam"]
    ordering = ["-publicatiedatum"]

    def get_queryset(self):
        qs = Aanbesteding.objects.prefetch_related(
            "gemma_componenten",
            "relevante_pakketten__leverancier",
        ).select_related("organisatie")

        # Filter op gemeente (fuzzy-match op aanbestedende_dienst)
        gemeente = self.request.query_params.get("gemeente")
        if gemeente:
            qs = qs.filter(aanbestedende_dienst__icontains=gemeente)

        # Filter op CPV-code
        cpv = self.request.query_params.get("cpv")
        if cpv:
            qs = qs.filter(cpv_codes__contains=[cpv])

        # Filter op GEMMA-component naam (directe naam-match)
        gemma = self.request.query_params.get("gemma")
        if gemma:
            qs = qs.filter(gemma_componenten__naam__icontains=gemma).distinct()

        # Filter op pakket-UUID: haal GEMMA-componenten van dat pakket op en
        # toon aanbestedingen die overeenkomen
        pakket_id = self.request.query_params.get("pakket")
        if pakket_id:
            from apps.pakketten.models import Pakket as PakketModel
            try:
                pakket = PakketModel.objects.prefetch_related("gemma_componenten").get(id=pakket_id)
                gemma_ids = list(pakket.gemma_componenten.values_list("id", flat=True))
                if gemma_ids:
                    qs = qs.filter(gemma_componenten__id__in=gemma_ids).distinct()
                else:
                    # Pakket heeft geen GEMMA-koppeling: zoek op pakketnaam
                    qs = qs.filter(naam__icontains=pakket.naam[:60]).distinct()
            except (PakketModel.DoesNotExist, Exception):
                qs = qs.none()

        # Filter op leverancier-UUID: toon aanbestedingen die aansluiten bij
        # de GEMMA-componenten van de pakketten van deze leverancier
        leverancier_id = self.request.query_params.get("leverancier")
        if leverancier_id:
            from apps.pakketten.models import Pakket as PakketModel
            gemma_ids = list(
                PakketModel.objects.filter(leverancier_id=leverancier_id)
                .values_list("gemma_componenten__id", flat=True)
                .distinct()
            )
            # Filter None-waarden (pakketten zonder GEMMA-koppeling geven NULL)
            gemma_ids = [g for g in gemma_ids if g is not None]
            if gemma_ids:
                qs = qs.filter(gemma_componenten__id__in=gemma_ids).distinct()
            else:
                # Leverancier heeft nog geen GEMMA-koppelingen: toon recente aanbestedingen
                pass  # Geen extra filter — toon alles

        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AanbestedingenDetailSerializer
        return AanbestedingenListSerializer

    def list(self, request, *args, **kwargs):
        """
        Geeft een gepagineerde lijst van recente ICT-aanbestedingen.
        Standaard: laatste 25 resultaten gesorteerd op publicatiedatum.

        Auto-bootstrap: als de database leeg is, wordt eenmalig gesynchroniseerd
        vanuit TenderNed (of demo-data indien TENDERNED_DEMO_MODE=True).
        """
        limit = min(int(request.query_params.get("limit", 25)), 50)
        qs = self.filter_queryset(self.get_queryset())

        # Auto-bootstrap: DB leeg en geen context-filter actief → sync eenmalig
        context_filters = ("gemeente", "pakket", "leverancier", "gemma", "cpv", "search")
        if not qs.exists() and not any(request.query_params.get(f) for f in context_filters):
            self._bootstrap_indien_leeg()
            qs = self.filter_queryset(self.get_queryset())

        if "limit" in request.query_params:
            serializer = self.get_serializer(qs[:limit], many=True)
            return Response({
                "count": qs.count(),
                "results": serializer.data,
            })

        return super().list(request, *args, **kwargs)

    def _bootstrap_indien_leeg(self):
        """
        Synchroniseer TenderNed data eenmalig als de database leeg is.
        Gebruikt Django cache als mutex om herhaalde calls te voorkomen.
        """
        from django.core.cache import cache
        cache_key = "tenderned_bootstrap_done"
        if cache.get(cache_key):
            return
        # Markeer als bezig (1 uur cooldown ook bij mislukking)
        cache.set(cache_key, True, timeout=3600)
        try:
            from apps.aanbestedingen.tasks import sync_tenderned
            sync_tenderned(dagen_terug=30, max_resultaten=100)
            logger.info("TenderNed auto-bootstrap geslaagd")
        except Exception as exc:
            logger.warning("TenderNed auto-bootstrap mislukt: %s", exc)

    def sync(self, request):
        """Handmatige TenderNed sync (alleen functioneel beheerder)."""
        from apps.aanbestedingen.tasks import sync_tenderned
        resultaat = sync_tenderned.delay()
        return Response({"detail": "Synchronisatie gestart.", "task_id": str(resultaat.id)})
