"""Tests voor de GEMMA architectuurkaart API (issue #12)."""
import pytest
from django.urls import reverse

from apps.architectuur.models import PakketGemmaComponent
from apps.pakketten.models import PakketGebruik

pytestmark = pytest.mark.django_db


# ========================
# GET /api/v1/gemma/kaart/
# ========================

class TestGemmaKaartView:
    """Architectuurkaart endpoint retourneert componenthiëarchie met pakketten."""

    def test_anoniem_toegankelijk(self, api_client, gemma_component):
        url = reverse("api:gemma-kaart")
        response = api_client.get(url)
        assert response.status_code == 200

    def test_retourneert_root_componenten(self, api_client, gemma_component, gemma_child):
        """Root-componenten (zonder parent) staan in 'componenten'."""
        url = reverse("api:gemma-kaart")
        response = api_client.get(url)
        assert response.status_code == 200
        namen = [c["naam"] for c in response.data["componenten"]]
        assert "Zaaksysteem" in namen
        # Child hoort niet op root-niveau
        assert "Zaakafhandelservice" not in namen

    def test_kinderen_genest_in_parent(self, api_client, gemma_component, gemma_child):
        """Children worden genest binnen hun parent."""
        url = reverse("api:gemma-kaart")
        response = api_client.get(url)
        zaaksysteem = next(
            c for c in response.data["componenten"] if c["naam"] == "Zaaksysteem"
        )
        kind_namen = [k["naam"] for k in zaaksysteem["kinderen"]]
        assert "Zaakafhandelservice" in kind_namen

    def test_verplichte_velden_aanwezig(self, api_client, gemma_component):
        url = reverse("api:gemma-kaart")
        response = api_client.get(url)
        component = next(
            c for c in response.data["componenten"] if c["naam"] == "Zaaksysteem"
        )
        for veld in ["id", "naam", "archimate_id", "type", "type_display", "kinderen", "pakketten"]:
            assert veld in component, f"Veld '{veld}' ontbreekt"

    def test_pakketten_leeg_zonder_koppeling(self, api_client, gemma_component):
        url = reverse("api:gemma-kaart")
        response = api_client.get(url)
        zaaksysteem = next(
            c for c in response.data["componenten"] if c["naam"] == "Zaaksysteem"
        )
        assert zaaksysteem["pakketten"] == []

    def test_actief_pakket_zichtbaar_anoniem(self, api_client, gemma_component, pakket):
        """Anonieme gebruikers zien actieve pakketten gekoppeld aan component."""
        PakketGemmaComponent.objects.create(pakket=pakket, gemma_component=gemma_component)
        url = reverse("api:gemma-kaart")
        response = api_client.get(url)
        zaaksysteem = next(
            c for c in response.data["componenten"] if c["naam"] == "Zaaksysteem"
        )
        pakket_namen = [p["naam"] for p in zaaksysteem["pakketten"]]
        assert "Suite4Gemeenten" in pakket_namen

    def test_concept_pakket_niet_zichtbaar_anoniem(self, api_client, gemma_component, concept_pakket):
        """Concept-pakketten zijn niet zichtbaar voor anonieme gebruikers."""
        PakketGemmaComponent.objects.create(pakket=concept_pakket, gemma_component=gemma_component)
        url = reverse("api:gemma-kaart")
        response = api_client.get(url)
        zaaksysteem = next(
            c for c in response.data["componenten"] if c["naam"] == "Zaaksysteem"
        )
        pakket_namen = [p["naam"] for p in zaaksysteem["pakketten"]]
        assert "NieuwPakket" not in pakket_namen

    def test_eigen_pakketgebruik_zichtbaar_ingelogd(
        self, auth_client, gebruik_beheerder, gemma_component, pakket, pakket_gebruik
    ):
        """Geauthenticeerde gebruiker ziet eigen pakketgebruik per component."""
        PakketGemmaComponent.objects.create(pakket=pakket, gemma_component=gemma_component)
        url = reverse("api:gemma-kaart")
        response = auth_client.get(url)
        assert response.status_code == 200
        zaaksysteem = next(
            c for c in response.data["componenten"] if c["naam"] == "Zaaksysteem"
        )
        pakket_namen = [p["naam"] for p in zaaksysteem["pakketten"]]
        assert "Suite4Gemeenten" in pakket_namen

    def test_status_gebruik_in_response(
        self, auth_client, gemma_component, pakket, pakket_gebruik
    ):
        """Status_gebruik van het pakketgebruik is opgenomen."""
        PakketGemmaComponent.objects.create(pakket=pakket, gemma_component=gemma_component)
        url = reverse("api:gemma-kaart")
        response = auth_client.get(url)
        zaaksysteem = next(
            c for c in response.data["componenten"] if c["naam"] == "Zaaksysteem"
        )
        suite = next(p for p in zaaksysteem["pakketten"] if p["naam"] == "Suite4Gemeenten")
        assert suite["status_gebruik"] == "in_gebruik"

    def test_pakket_andere_organisatie_niet_zichtbaar(
        self, auth_client, gebruik_beheerder, gemma_component, pakket, gemeente2
    ):
        """Pakketgebruik van andere organisatie is niet zichtbaar."""
        PakketGemmaComponent.objects.create(pakket=pakket, gemma_component=gemma_component)
        # Pakket van gemeente2
        PakketGebruik.objects.create(
            pakket=pakket, organisatie=gemeente2, status=PakketGebruik.Status.IN_GEBRUIK
        )
        url = reverse("api:gemma-kaart")
        response = auth_client.get(url)
        zaaksysteem = next(
            c for c in response.data["componenten"] if c["naam"] == "Zaaksysteem"
        )
        # Eigen organisatie (gemeente) heeft geen pakketgebruik -> leeg
        assert zaaksysteem["pakketten"] == []

    def test_type_display_aanwezig(self, api_client, gemma_component):
        url = reverse("api:gemma-kaart")
        response = api_client.get(url)
        zaaksysteem = next(
            c for c in response.data["componenten"] if c["naam"] == "Zaaksysteem"
        )
        assert zaaksysteem["type_display"] == "Applicatiecomponent"


# ========================
# GET /api/v1/gemma/componenten/ (bestaande endpoint)
# ========================

class TestGemmaComponentenAPI:
    def test_lijst_root_componenten(self, api_client, gemma_component, gemma_child):
        url = reverse("api:gemma-component-list")
        response = api_client.get(url, {"parent__isnull": True})
        assert response.status_code == 200
        namen = [c["naam"] for c in response.data["results"]]
        assert "Zaaksysteem" in namen
        assert "Zaakafhandelservice" not in namen

    def test_detail_bevat_kinderen(self, api_client, gemma_component, gemma_child):
        url = reverse("api:gemma-component-detail", kwargs={"pk": gemma_component.pk})
        response = api_client.get(url)
        assert response.status_code == 200
        kind_namen = [k["naam"] for k in response.data["children"]]
        assert "Zaakafhandelservice" in kind_namen

    def test_zoeken_op_naam(self, api_client, gemma_component, gemma_child):
        url = reverse("api:gemma-component-list")
        response = api_client.get(url, {"search": "Zaak"})
        assert response.status_code == 200
        assert len(response.data["results"]) >= 1
