"""Tests voor publieke API endpoints."""
import pytest
from django.urls import reverse

from apps.content.models import Pagina
from apps.organisaties.models import Organisatie
from apps.pakketten.models import Pakket

pytestmark = pytest.mark.django_db


# ========================
# Pakketten API
# ========================

class TestPakkettenAPI:
    def test_lijst_pakketten_zonder_auth(self, api_client, pakket, concept_pakket):
        url = reverse("api:pakket-list")
        response = api_client.get(url)
        assert response.status_code == 200
        # Publiek ziet ALLEEN actieve pakketten, niet concept (fix #25)
        namen = [p["naam"] for p in response.data["results"]]
        assert "Suite4Gemeenten" in namen
        assert "NieuwPakket" not in namen

    def test_pakket_detail(self, api_client, pakket):
        url = reverse("api:pakket-detail", kwargs={"pk": pakket.pk})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["naam"] == "Suite4Gemeenten"
        assert response.data["versie"] == "5.0"
        assert "leverancier" in response.data

    def test_pakket_zoeken_op_naam(self, api_client, pakket, pakket2):
        url = reverse("api:pakket-list")
        response = api_client.get(url, {"search": "Suite"})
        assert response.status_code == 200
        namen = [p["naam"] for p in response.data["results"]]
        assert "Suite4Gemeenten" in namen
        assert "eBurgerzaken" not in namen

    def test_pakket_filteren_op_licentievorm(self, api_client, pakket, pakket2):
        url = reverse("api:pakket-list")
        response = api_client.get(url, {"licentievorm": "saas"})
        assert response.status_code == 200
        namen = [p["naam"] for p in response.data["results"]]
        assert "Suite4Gemeenten" in namen
        assert "eBurgerzaken" not in namen

    def test_pakket_filteren_op_status(self, api_client, pakket, concept_pakket):
        url = reverse("api:pakket-list")
        response = api_client.get(url, {"status": "actief"})
        assert response.status_code == 200
        namen = [p["naam"] for p in response.data["results"]]
        assert "Suite4Gemeenten" in namen
        assert "NieuwPakket" not in namen

    def test_pakket_aanmaken_zonder_auth_verboden(self, api_client, leverancier):
        url = reverse("api:pakket-list")
        data = {"naam": "Nieuw", "leverancier": str(leverancier.pk)}
        response = api_client.post(url, data)
        assert response.status_code == 401

    def test_pakket_detail_bevat_aantal_gebruikers(self, api_client, pakket, pakket_gebruik):
        url = reverse("api:pakket-detail", kwargs={"pk": pakket.pk})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["aantal_gebruikers"] >= 1

    def test_pakket_detail_bevat_gebruikende_organisaties(self, api_client, pakket, pakket_gebruik):
        url = reverse("api:pakket-detail", kwargs={"pk": pakket.pk})
        response = api_client.get(url)
        assert response.status_code == 200
        org_namen = [o["naam"] for o in response.data["gebruikende_organisaties"]]
        assert "Gemeente Utrecht" in org_namen

    def test_pakketten_ordering(self, api_client, pakket, pakket2):
        url = reverse("api:pakket-list")
        response = api_client.get(url, {"ordering": "naam"})
        assert response.status_code == 200
        namen = [p["naam"] for p in response.data["results"]]
        assert namen == sorted(namen)

    def test_verouderd_pakket_niet_zichtbaar_voor_publiek(self, api_client, db, leverancier):
        Pakket.objects.create(
            naam="OudPakket",
            status=Pakket.Status.VEROUDERD,
            leverancier=leverancier,
        )
        url = reverse("api:pakket-list")
        response = api_client.get(url)
        namen = [p["naam"] for p in response.data["results"]]
        assert "OudPakket" not in namen


# ========================
# Organisaties API
# ========================

class TestOrganisatiesAPI:
    def test_lijst_organisaties(self, api_client, gemeente, leverancier):
        url = reverse("api:organisatie-list")
        response = api_client.get(url)
        assert response.status_code == 200
        namen = [o["naam"] for o in response.data["results"]]
        assert "Gemeente Utrecht" in namen
        assert "Centric" in namen

    def test_concept_organisatie_niet_zichtbaar_publiek(self, api_client, concept_organisatie):
        url = reverse("api:organisatie-list")
        response = api_client.get(url)
        namen = [o["naam"] for o in response.data["results"]]
        assert "Nieuwe Leverancier BV" not in namen

    def test_organisatie_detail(self, api_client, gemeente):
        url = reverse("api:organisatie-detail", kwargs={"pk": gemeente.pk})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["naam"] == "Gemeente Utrecht"
        assert "contactpersonen" in response.data
        assert "aantal_pakketten" in response.data

    def test_organisatie_zoeken(self, api_client, gemeente, leverancier):
        url = reverse("api:organisatie-list")
        response = api_client.get(url, {"search": "Utrecht"})
        assert response.status_code == 200
        namen = [o["naam"] for o in response.data["results"]]
        assert "Gemeente Utrecht" in namen
        assert "Centric" not in namen

    def test_organisatie_filteren_op_type(self, api_client, gemeente, leverancier):
        url = reverse("api:organisatie-list")
        response = api_client.get(url, {"type": "gemeente"})
        assert response.status_code == 200
        types = [o["type"] for o in response.data["results"]]
        assert all(t == "gemeente" for t in types)

    def test_organisatie_aanmaken_vereist_auth(self, api_client):
        url = reverse("api:organisatie-list")
        response = api_client.post(url, {"naam": "Test", "type": "leverancier"})
        assert response.status_code == 401

    def test_organisatie_aanmaken_als_ingelogd(self, auth_client, gebruik_beheerder):
        url = reverse("api:organisatie-list")
        data = {"naam": "Nieuw SWV", "type": "samenwerkingsverband"}
        response = auth_client.post(url, data)
        assert response.status_code == 201
        org = Organisatie.objects.get(naam="Nieuw SWV")
        assert org.status == Organisatie.Status.CONCEPT
        assert org.geregistreerd_door == gebruik_beheerder


# ========================
# Standaarden API
# ========================

class TestStandaardenAPI:
    def test_lijst_standaarden(self, api_client, standaard, standaard2):
        url = reverse("api:standaard-list")
        response = api_client.get(url)
        assert response.status_code == 200
        namen = [s["naam"] for s in response.data["results"]]
        assert "DigiD" in namen
        assert "StUF-BG" in namen

    def test_standaard_detail(self, api_client, standaard):
        url = reverse("api:standaard-detail", kwargs={"pk": standaard.pk})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["naam"] == "DigiD"

    def test_standaarden_filteren_op_type(self, api_client, standaard, standaard2):
        url = reverse("api:standaard-list")
        response = api_client.get(url, {"type": "verplicht"})
        assert response.status_code == 200
        namen = [s["naam"] for s in response.data["results"]]
        assert "DigiD" in namen
        assert "StUF-BG" not in namen

    def test_standaarden_read_only(self, auth_client, standaard):
        url = reverse("api:standaard-list")
        response = auth_client.post(url, {"naam": "Nieuw"})
        assert response.status_code == 405  # Method Not Allowed


# ========================
# GEMMA Componenten API
# ========================

class TestGemmaComponentenAPI:
    def test_lijst_componenten(self, api_client, gemma_component, gemma_child):
        url = reverse("api:gemma-component-list")
        response = api_client.get(url)
        assert response.status_code == 200

    def test_component_detail(self, api_client, gemma_component):
        url = reverse("api:gemma-component-detail", kwargs={"pk": gemma_component.pk})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["naam"] == "Zaaksysteem"

    def test_filteren_op_root_componenten(self, api_client, gemma_component, gemma_child):
        url = reverse("api:gemma-component-list")
        response = api_client.get(url, {"parent__isnull": True})
        assert response.status_code == 200
        # GemmaComponentViewSet heeft pagination_class = None → flat list
        namen = [c["naam"] for c in response.data]
        assert "Zaaksysteem" in namen
        assert "Zaakafhandelservice" not in namen


# ========================
# Content API
# ========================

class TestContentAPI:
    def test_lijst_paginas(self, api_client, pagina):
        url = reverse("api:pagina-list")
        response = api_client.get(url)
        assert response.status_code == 200

    def test_pagina_detail_by_slug(self, api_client, pagina):
        url = reverse("api:pagina-detail", kwargs={"slug": "over-ons"})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["titel"] == "Over ons"

    def test_lijst_nieuwsberichten(self, api_client, nieuwsbericht):
        url = reverse("api:nieuwsbericht-list")
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data["results"]) >= 1

    def test_ongepubliceerde_pagina_niet_zichtbaar(self, api_client, db):
        Pagina.objects.create(
            titel="Verborgen", slug="verborgen", inhoud="Test", gepubliceerd=False
        )
        url = reverse("api:pagina-list")
        response = api_client.get(url)
        titels = [p["titel"] for p in response.data["results"]]
        assert "Verborgen" not in titels
