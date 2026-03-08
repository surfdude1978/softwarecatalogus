"""Pytest fixtures voor de Softwarecatalogus backend tests."""
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.gebruikers.models import User
from apps.organisaties.models import Organisatie, Contactpersoon
from apps.pakketten.models import Pakket, PakketGebruik, Koppeling
from apps.standaarden.models import Standaard, PakketStandaard
from apps.architectuur.models import GemmaComponent, PakketGemmaComponent
from apps.documenten.models import Document
from apps.content.models import Pagina, Nieuwsbericht


# ========================
# Organisaties
# ========================

@pytest.fixture
def gemeente(db):
    return Organisatie.objects.create(
        naam="Gemeente Utrecht",
        type=Organisatie.Type.GEMEENTE,
        status=Organisatie.Status.ACTIEF,
        oin="00000001002306608000",
    )


@pytest.fixture
def gemeente2(db):
    return Organisatie.objects.create(
        naam="Gemeente Amsterdam",
        type=Organisatie.Type.GEMEENTE,
        status=Organisatie.Status.ACTIEF,
        oin="00000004003214345000",
    )


@pytest.fixture
def leverancier(db):
    return Organisatie.objects.create(
        naam="Centric",
        type=Organisatie.Type.LEVERANCIER,
        status=Organisatie.Status.ACTIEF,
        website="https://www.centric.eu",
    )


@pytest.fixture
def concept_organisatie(db):
    return Organisatie.objects.create(
        naam="Nieuwe Leverancier BV",
        type=Organisatie.Type.LEVERANCIER,
        status=Organisatie.Status.CONCEPT,
    )


# ========================
# Users
# ========================

@pytest.fixture
def gebruiker_publiek(db, gemeente):
    return User.objects.create_user(
        email="publiek@example.com",
        naam="Publieke Gebruiker",
        password="TestWachtwoord123!",
        organisatie=gemeente,
        rol=User.Rol.PUBLIEK,
        status=User.Status.ACTIEF,
    )


@pytest.fixture
def gebruik_beheerder(db, gemeente):
    return User.objects.create_user(
        email="gebruik@utrecht.nl",
        naam="Gebruik Beheerder",
        password="TestWachtwoord123!",
        organisatie=gemeente,
        rol=User.Rol.GEBRUIK_BEHEERDER,
        status=User.Status.ACTIEF,
    )


@pytest.fixture
def aanbod_beheerder(db, leverancier):
    return User.objects.create_user(
        email="aanbod@centric.eu",
        naam="Aanbod Beheerder",
        password="TestWachtwoord123!",
        organisatie=leverancier,
        rol=User.Rol.AANBOD_BEHEERDER,
        status=User.Status.ACTIEF,
    )


@pytest.fixture
def functioneel_beheerder(db):
    return User.objects.create_user(
        email="admin@vngrealisatie.nl",
        naam="Functioneel Beheerder",
        password="TestWachtwoord123!",
        rol=User.Rol.FUNCTIONEEL_BEHEERDER,
        status=User.Status.ACTIEF,
    )


@pytest.fixture
def inactieve_gebruiker(db, gemeente):
    return User.objects.create_user(
        email="inactief@example.com",
        naam="Inactieve Gebruiker",
        password="TestWachtwoord123!",
        organisatie=gemeente,
        rol=User.Rol.GEBRUIK_BEHEERDER,
        status=User.Status.INACTIEF,
    )


@pytest.fixture
def wachtend_gebruiker(db, gemeente):
    return User.objects.create_user(
        email="wachtend@example.com",
        naam="Wachtende Gebruiker",
        password="TestWachtwoord123!",
        organisatie=gemeente,
        rol=User.Rol.GEBRUIK_BEHEERDER,
        status=User.Status.WACHT_OP_FIATTERING,
    )


# ========================
# API Client helpers
# ========================

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, gebruik_beheerder):
    """API client geauthenticeerd als gebruik-beheerder."""
    refresh = RefreshToken.for_user(gebruik_beheerder)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def aanbod_client(api_client, aanbod_beheerder):
    """API client geauthenticeerd als aanbod-beheerder."""
    refresh = RefreshToken.for_user(aanbod_beheerder)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def admin_client(api_client, functioneel_beheerder):
    """API client geauthenticeerd als functioneel beheerder."""
    refresh = RefreshToken.for_user(functioneel_beheerder)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


# ========================
# Pakketten
# ========================

@pytest.fixture
def pakket(db, leverancier):
    return Pakket.objects.create(
        naam="Suite4Gemeenten",
        versie="5.0",
        status=Pakket.Status.ACTIEF,
        beschrijving="Compleet pakket voor gemeentelijke dienstverlening.",
        leverancier=leverancier,
        licentievorm=Pakket.Licentievorm.SAAS,
        website_url="https://www.centric.eu/suite4gemeenten",
    )


@pytest.fixture
def pakket2(db, leverancier):
    return Pakket.objects.create(
        naam="eBurgerzaken",
        versie="3.2",
        status=Pakket.Status.ACTIEF,
        beschrijving="Burgerzaken applicatie.",
        leverancier=leverancier,
        licentievorm=Pakket.Licentievorm.COMMERCIEEL,
    )


@pytest.fixture
def concept_pakket(db, leverancier):
    return Pakket.objects.create(
        naam="NieuwPakket",
        status=Pakket.Status.CONCEPT,
        leverancier=leverancier,
    )


@pytest.fixture
def pakket_gebruik(db, pakket, gemeente):
    return PakketGebruik.objects.create(
        pakket=pakket,
        organisatie=gemeente,
        status=PakketGebruik.Status.IN_GEBRUIK,
    )


@pytest.fixture
def pakket_gebruik2(db, pakket2, gemeente):
    return PakketGebruik.objects.create(
        pakket=pakket2,
        organisatie=gemeente,
        status=PakketGebruik.Status.IN_GEBRUIK,
    )


# ========================
# Standaarden
# ========================

@pytest.fixture
def standaard(db):
    return Standaard.objects.create(
        naam="DigiD",
        type=Standaard.Type.VERPLICHT,
        versie="2.0",
        beschrijving="Digitale identiteit voor burgers.",
    )


@pytest.fixture
def standaard2(db):
    return Standaard.objects.create(
        naam="StUF-BG",
        type=Standaard.Type.AANBEVOLEN,
        versie="3.10",
    )


# ========================
# GEMMA Componenten
# ========================

@pytest.fixture
def gemma_component(db):
    return GemmaComponent.objects.create(
        naam="Zaaksysteem",
        archimate_id="id-gemma-001",
        type=GemmaComponent.Type.APPLICATIE_COMPONENT,
        beschrijving="Centraal zaakregistratiesysteem.",
    )


@pytest.fixture
def gemma_child(db, gemma_component):
    return GemmaComponent.objects.create(
        naam="Zaakafhandelservice",
        archimate_id="id-gemma-002",
        type=GemmaComponent.Type.APPLICATIE_SERVICE,
        parent=gemma_component,
    )


# ========================
# Content
# ========================

@pytest.fixture
def pagina(db):
    return Pagina.objects.create(
        titel="Over ons",
        slug="over-ons",
        inhoud="De Softwarecatalogus is een platform voor gemeenten.",
        gepubliceerd=True,
    )


@pytest.fixture
def nieuwsbericht(db):
    from django.utils import timezone
    return Nieuwsbericht.objects.create(
        titel="Nieuwe versie beschikbaar",
        slug="nieuwe-versie",
        samenvatting="De catalogus is vernieuwd.",
        inhoud="Uitgebreide beschrijving van de vernieuwing.",
        gepubliceerd=True,
        publicatie_datum=timezone.now(),
    )
