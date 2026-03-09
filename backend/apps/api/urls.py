"""API v1 URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import admin_views, export_views, help_views, views
from . import search_views as views_search

app_name = "api"

router = DefaultRouter()

# Publieke endpoints
router.register(r"aanbestedingen", views.AanbestedingenViewSet, basename="aanbesteding")
router.register(r"pakketten", views.PakketViewSet, basename="pakket")
router.register(r"organisaties", views.OrganisatieViewSet, basename="organisatie")
router.register(r"standaarden", views.StandaardViewSet, basename="standaard")
router.register(r"gemma/componenten", views.GemmaComponentViewSet, basename="gemma-component")
router.register(r"nieuws", views.NieuwsberichtViewSet, basename="nieuwsbericht")
router.register(r"paginas", views.PaginaViewSet, basename="pagina")

# Beveiligde endpoints
router.register(r"mijn-organisatie/pakketoverzicht", views.MijnPakketOverzichtViewSet, basename="mijn-pakketoverzicht")
router.register(r"mijn-organisatie/koppelingen", views.KoppelingViewSet, basename="koppeling")
router.register(r"documenten", views.DocumentViewSet, basename="document")
router.register(r"profiel", views.ProfielViewSet, basename="profiel")
router.register(r"notificaties", views.NotificatieViewSet, basename="notificatie")

# Admin endpoints
router.register(r"admin/organisaties", views.AdminOrganisatieViewSet, basename="admin-organisatie")
router.register(r"admin/gebruikers", views.AdminGebruikerViewSet, basename="admin-gebruiker")

urlpatterns = [
    path("", include(router.urls)),
    # Gluren bij de buren
    path(
        "gemeenten/<uuid:gemeente_id>/pakketoverzicht/",
        views.GemeentePakketOverzichtViewSet.as_view({"get": "list"}),
        name="gemeente-pakketoverzicht",
    ),
    # Auth endpoints
    path("auth/", include("apps.api.auth_urls")),
    # GEMMA architectuurkaart
    path("gemma/kaart/", views.GemmaKaartView.as_view(), name="gemma-kaart"),
    # Zoeken (Meilisearch)
    path("zoek/", views_search.ZoekView.as_view(), name="zoek"),
    # Export endpoints
    path("export/pakketten.csv", export_views.ExportPakkettenCSV.as_view(), name="export-pakketten-csv"),
    path("export/pakketten.xlsx", export_views.ExportPakkettenExcel.as_view(), name="export-pakketten-xlsx"),
    path("export/pakketoverzicht.csv", export_views.ExportPakketOverzichtCSV.as_view(), name="export-overzicht-csv"),
    path("export/pakketoverzicht.xlsx", export_views.ExportPakketOverzichtExcel.as_view(), name="export-overzicht-xlsx"),  # noqa: E501
    path("export/pakketoverzicht.ameff", export_views.ExportPakketOverzichtAMEFF.as_view(), name="export-overzicht-ameff"),  # noqa: E501
    # Admin: GEMMA AMEFF import
    path("admin/gemma/importeer/", admin_views.GemmaImportView.as_view(), name="admin-gemma-import"),
    # Admin: Audit log export (alleen functioneel beheerder)
    path("admin/auditlog.csv", export_views.ExportAuditLogCSV.as_view(), name="export-auditlog-csv"),
    # Help AI-assistent (publiek toegankelijk, rate-limited)
    path("help/vraag/", help_views.HelpVraagView.as_view(), name="help-vraag"),
]
