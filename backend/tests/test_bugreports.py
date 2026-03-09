"""Tests voor bugfixes #24 (zoeken werkt niet) en #25 (concept pakketten publiek zichtbaar)."""
from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def leverancier(db):
    from apps.organisaties.models import Organisatie
    return Organisatie.objects.create(
        naam="Test Leverancier BV",
        type="leverancier",
        status="actief",
    )


@pytest.fixture
def actief_pakket(db, leverancier):
    from apps.pakketten.models import Pakket
    return Pakket.objects.create(
        naam="Actief Pakket",
        beschrijving="Een actief pakket voor gemeenten.",
        status="actief",
        leverancier=leverancier,
        licentievorm="saas",
    )


@pytest.fixture
def concept_pakket(db, leverancier):
    from apps.pakketten.models import Pakket
    return Pakket.objects.create(
        naam="Concept Pakket",
        beschrijving="Nog niet goedgekeurd pakket.",
        status="concept",
        leverancier=leverancier,
        licentievorm="commercieel",
    )


# ── Bug #25: concept-pakketten publiek zichtbaar ──────────────────────────────

class TestConceptPakkettenPubliekZichtbaar:
    """Issue #25: concept-pakketten mogen niet zichtbaar zijn voor anonieme gebruikers."""

    def test_anoniem_ziet_geen_concept_pakket(self, api_client, actief_pakket, concept_pakket):
        url = reverse("api:pakket-list")
        response = api_client.get(url)
        assert response.status_code == 200
        namen = [p["naam"] for p in response.data["results"]]
        assert actief_pakket.naam in namen
        assert concept_pakket.naam not in namen

    def test_anoniem_kan_concept_detail_niet_ophalen(self, api_client, concept_pakket):
        url = reverse("api:pakket-detail", kwargs={"pk": str(concept_pakket.pk)})
        response = api_client.get(url)
        # Concept-pakket staat niet in de queryset voor anonieme gebruikers
        assert response.status_code == 404

    def test_anoniem_ziet_actief_pakket(self, api_client, actief_pakket):
        url = reverse("api:pakket-list")
        response = api_client.get(url)
        assert response.status_code == 200
        namen = [p["naam"] for p in response.data["results"]]
        assert actief_pakket.naam in namen

    def test_beheerder_ziet_concept_pakket(self, admin_client, actief_pakket, concept_pakket):
        """Ingelogde beheerder ziet wel concept-pakketten."""
        url = reverse("api:pakket-list")
        response = admin_client.get(url)
        assert response.status_code == 200
        namen = [p["naam"] for p in response.data["results"]]
        assert actief_pakket.naam in namen
        assert concept_pakket.naam in namen

    def test_filter_op_status_concept_geeft_lege_lijst_voor_anoniem(
        self, api_client, concept_pakket
    ):
        """?status=concept geeft lege lijst voor anonieme gebruiker."""
        url = reverse("api:pakket-list") + "?status=concept"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 0


# ── Bug #24: zoek-endpoint ORM-fallback ──────────────────────────────────────

class TestZoekEndpointOrmFallback:
    """Issue #24: zoeken werkt altijd, ook zonder Meilisearch."""

    def test_zoek_vereist_q_parameter(self, api_client):
        url = reverse("api:zoek")
        response = api_client.get(url)
        assert response.status_code == 400

    def test_zoek_via_orm_fallback_bij_meilisearch_fout(
        self, api_client, actief_pakket
    ):
        """Als Meilisearch niet beschikbaar is, valt het endpoint terug op ORM."""
        url = reverse("api:zoek") + "?q=actief"
        with patch(
            "apps.pakketten.search.get_pakketten_index",
            side_effect=Exception("Meilisearch not available"),
        ):
            response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["total"] >= 1
        namen = [h["naam"] for h in response.data["hits"]]
        assert actief_pakket.naam in namen

    def test_orm_fallback_bevat_geen_concept_pakketten(
        self, api_client, actief_pakket, concept_pakket
    ):
        """ORM-fallback toont geen concept-pakketten aan publiek."""
        url = reverse("api:zoek") + "?q=pakket"
        with patch(
            "apps.pakketten.search.get_pakketten_index",
            side_effect=Exception("Meilisearch not available"),
        ):
            response = api_client.get(url)

        assert response.status_code == 200
        namen = [h["naam"] for h in response.data["hits"]]
        assert concept_pakket.naam not in namen
        assert actief_pakket.naam in namen

    def test_orm_fallback_zoekt_op_naam(self, api_client, actief_pakket):
        url = reverse("api:zoek") + "?q=Actief"
        with patch(
            "apps.pakketten.search.get_pakketten_index",
            side_effect=Exception("Meilisearch not available"),
        ):
            response = api_client.get(url)

        assert response.status_code == 200
        namen = [h["naam"] for h in response.data["hits"]]
        assert actief_pakket.naam in namen

    def test_orm_fallback_zoekt_op_beschrijving(self, api_client, actief_pakket):
        url = reverse("api:zoek") + "?q=gemeenten"
        with patch(
            "apps.pakketten.search.get_pakketten_index",
            side_effect=Exception("Meilisearch not available"),
        ):
            response = api_client.get(url)

        assert response.status_code == 200
        namen = [h["naam"] for h in response.data["hits"]]
        assert actief_pakket.naam in namen

    def test_orm_fallback_zoekt_op_leverancier_naam(self, api_client, actief_pakket):
        url = reverse("api:zoek") + "?q=Test+Leverancier"
        with patch(
            "apps.pakketten.search.get_pakketten_index",
            side_effect=Exception("Meilisearch not available"),
        ):
            response = api_client.get(url)

        assert response.status_code == 200
        namen = [h["naam"] for h in response.data["hits"]]
        assert actief_pakket.naam in namen

    def test_orm_fallback_filter_licentievorm(self, api_client, actief_pakket, concept_pakket):
        """ORM-fallback respecteert licentievorm-filter."""
        url = reverse("api:zoek") + "?q=pakket&licentievorm=saas"
        with patch(
            "apps.pakketten.search.get_pakketten_index",
            side_effect=Exception("Meilisearch not available"),
        ):
            response = api_client.get(url)

        assert response.status_code == 200
        namen = [h["naam"] for h in response.data["hits"]]
        assert actief_pakket.naam in namen
        # concept_pakket heeft licentievorm=commercieel, niet saas
        assert concept_pakket.naam not in namen

    def test_zoek_meilisearch_filter_bevat_alleen_actief(
        self, api_client, actief_pakket
    ):
        """Meilisearch-filter bevat alleen status=actief (niet concept)."""
        mock_index = MagicMock()
        mock_index.search.return_value = {
            "hits": [],
            "estimatedTotalHits": 0,
        }
        url = reverse("api:zoek") + "?q=test"
        with patch(
            "apps.pakketten.search.get_pakketten_index",
            return_value=mock_index,
        ):
            api_client.get(url)

        # Controleer dat de filter alleen 'actief' bevat, niet 'concept'
        call_args = mock_index.search.call_args
        used_filter = call_args[1].get("filter") or (
            call_args[0][1].get("filter") if len(call_args[0]) > 1 else ""
        )
        assert "actief" in used_filter
        assert "concept" not in used_filter
