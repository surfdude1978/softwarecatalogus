"""API v1 URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from . import search_views as views_search
from . import export_views
from . import admin_views

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
    # Zoeken (Meilisearch)
    path("zoek/", views_search.ZoekView.as_view(), name="zoek"),
    # Export endpoints
    path("export/pakketten.csv", export_views.ExportPakkettenCSV.as_view(), name="export-pakketten-csv"),
    path("export/pakketten.xlsx", export_views.ExportPakkettenExcel.as_view(), name="export-pakketten-xlsx"),
    path("export/pakketoverzicht.csv", export_views.ExportPakketOverzichtCSV.as_view(), name="export-overzicht-csv"),
    path("export/pakketoverzicht.xlsx", export_views.ExportPakketOverzichtExcel.as_view(), name="export-overzicht-xlsx"),
    path("export/pakketoverzicht.ameff", export_views.ExportPakketOverzichtAMEFF.as_view(), name="export-overzicht-ameff"),
    # Admin: GEMMA AMEFF import
    path("admin/gemma/importeer/", admin_views.GemmaImportView.as_view(), name="admin-gemma-import"),
    # Admin: Audit log export (alleen functioneel beheerder)
    path("admin/auditlog.csv", export_views.ExportAuditLogCSV.as_view(), name="export-auditlog-csv"),
]
