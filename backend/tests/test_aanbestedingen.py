"""Tests voor TenderNed aanbestedingen: client, taken en koppellogica."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta

from django.test import override_settings

from apps.aanbestedingen.client import (
    TenderNedClient,
    bepaal_gemma_componenten,
    DEMO_AANBESTEDINGEN,
    CPV_GEMMA_MAPPING,
    ICT_CPV_CODES,
)
from apps.aanbestedingen.models import Aanbesteding


pytestmark = pytest.mark.django_db


# ─────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────

@pytest.fixture
def client_demo():
    """TenderNedClient in demo-modus."""
    return TenderNedClient(demo_mode=True)


@pytest.fixture
def client_live():
    """TenderNedClient in live-modus (HTTP wordt gemockt)."""
    # demo_mode wordt vanuit settings overridden, dus expliciet op False zetten
    with override_settings(TENDERNED_DEMO_MODE=False):
        client = TenderNedClient(demo_mode=False, base_url="http://mock-tenderned/api")
        client.demo_mode = False  # Garantie dat demo-modus uit staat
        return client


@pytest.fixture
def aanbesteding(db):
    return Aanbesteding.objects.create(
        publicatiecode="TEST-001",
        naam="Test Zaaksysteem",
        aanbestedende_dienst="Gemeente Utrecht",
        aanbestedende_dienst_stad="Utrecht",
        type="europees",
        status="aankondiging",
        publicatiedatum=date.today(),
        cpv_codes=["72230000", "48100000"],
        cpv_omschrijvingen=["Software", "IT-diensten"],
        url_tenderned="https://www.tenderned.nl/aankondigingen/overzicht/TEST-001",
    )


# ─────────────────────────────────────────────────────────────────
# Tests: bepaal_gemma_componenten
# ─────────────────────────────────────────────────────────────────

class TestBepaalGemmaComponenten:
    def test_zaaksysteem_cpv(self):
        componenten = bepaal_gemma_componenten(["48100000"])
        assert "Zaaksysteem" in componenten

    def test_financieel_cpv(self):
        componenten = bepaal_gemma_componenten(["48400000"])
        assert "Financieel systeem" in componenten

    def test_meerdere_cpv_codes(self):
        componenten = bepaal_gemma_componenten(["48100000", "72600000"])
        assert "Zaaksysteem" in componenten
        assert "ICT-ondersteuning" in componenten

    def test_geen_match(self):
        componenten = bepaal_gemma_componenten(["99999999"])
        assert componenten == []

    def test_lege_lijst(self):
        componenten = bepaal_gemma_componenten([])
        assert componenten == []

    def test_it_diensten_cpv(self):
        componenten = bepaal_gemma_componenten(["72000000"])
        assert "IT-diensten" in componenten


# ─────────────────────────────────────────────────────────────────
# Tests: TenderNedClient – demo-modus
# ─────────────────────────────────────────────────────────────────

class TestTenderNedClientDemo:
    def test_demo_modus_geeft_demo_data(self, client_demo):
        resultaten = client_demo.haal_ict_aanbestedingen_op()
        assert len(resultaten) > 0
        assert resultaten == DEMO_AANBESTEDINGEN[:100]

    def test_demo_modus_respecteert_max_resultaten(self, client_demo):
        resultaten = client_demo.haal_ict_aanbestedingen_op(max_resultaten=3)
        assert len(resultaten) <= 3

    def test_demo_resultaten_bevatten_verplichte_velden(self, client_demo):
        resultaten = client_demo.haal_ict_aanbestedingen_op(max_resultaten=1)
        assert len(resultaten) > 0
        item = resultaten[0]
        assert "publicatiecode" in item
        assert "naam" in item
        assert "aanbestedende_dienst" in item
        assert "publicatiedatum" in item
        assert "cpv_codes" in item
        assert "url_tenderned" in item


# ─────────────────────────────────────────────────────────────────
# Tests: TenderNedClient – _extraheer_cpv_codes
# ─────────────────────────────────────────────────────────────────

class TestExtraheerCpvCodes:
    def setup_method(self):
        self.client = TenderNedClient(demo_mode=True)

    def test_cpv_als_string_lijst(self):
        item = {"cpvCodes": ["48000000", "72000000"]}
        codes = self.client._extraheer_cpv_codes(item)
        assert "48000000" in codes
        assert "72000000" in codes

    def test_cpv_als_dict_lijst_met_code_veld(self):
        item = {"cpvCodes": [{"code": "48000000"}, {"code": "72000000"}]}
        codes = self.client._extraheer_cpv_codes(item)
        assert "48000000" in codes

    def test_cpv_als_dict_lijst_met_cpvcode_veld(self):
        item = {"cpvCodes": [{"cpvCode": "72230000"}]}
        codes = self.client._extraheer_cpv_codes(item)
        assert "72230000" in codes

    def test_fallback_velden(self):
        item = {"cpv": ["72260000"]}
        codes = self.client._extraheer_cpv_codes(item)
        assert "72260000" in codes

    def test_classifications_veld(self):
        item = {"classifications": [{"id": "48100000"}]}
        codes = self.client._extraheer_cpv_codes(item)
        assert "48100000" in codes

    def test_leeg_item(self):
        codes = self.client._extraheer_cpv_codes({})
        assert codes == []

    def test_dedupliceert_codes(self):
        item = {"cpvCodes": ["48000000", "48000000", "48000000"]}
        codes = self.client._extraheer_cpv_codes(item)
        assert len(codes) == 1


# ─────────────────────────────────────────────────────────────────
# Tests: TenderNedClient – _is_ict_aanbesteding
# ─────────────────────────────────────────────────────────────────

class TestIsIctAanbesteding:
    def setup_method(self):
        self.client = TenderNedClient(demo_mode=True)

    def test_software_cpv_is_ict(self):
        assert self.client._is_ict_aanbesteding(["48000000"])

    def test_it_diensten_cpv_is_ict(self):
        assert self.client._is_ict_aanbesteding(["72230000"])

    def test_niet_ict_cpv(self):
        assert not self.client._is_ict_aanbesteding(["45000000"])  # Bouw

    def test_lege_lijst_geen_ict(self):
        assert not self.client._is_ict_aanbesteding([])

    def test_gemengde_lijst_met_ict(self):
        assert self.client._is_ict_aanbesteding(["45000000", "48100000"])


# ─────────────────────────────────────────────────────────────────
# Tests: TenderNedClient – _map_type
# ─────────────────────────────────────────────────────────────────

class TestMapType:
    def setup_method(self):
        self.client = TenderNedClient(demo_mode=True)

    def test_europees(self):
        assert self.client._map_type({"type": "Europees"}) == "europees"

    def test_nationaal(self):
        assert self.client._map_type({"type": "nationaal"}) == "nationaal"

    def test_eu_keyword(self):
        assert self.client._map_type({"procurementType": "EU above threshold"}) == "europees"

    def test_onbekend(self):
        assert self.client._map_type({}) == "onbekend"

    def test_aanbestedingstype_veld(self):
        assert self.client._map_type({"aanbestedingstype": "Europees"}) == "europees"


# ─────────────────────────────────────────────────────────────────
# Tests: TenderNedClient – _map_status
# ─────────────────────────────────────────────────────────────────

class TestMapStatus:
    def setup_method(self):
        self.client = TenderNedClient(demo_mode=True)

    def test_aankondiging_default(self):
        assert self.client._map_status({}) == "aankondiging"

    def test_gunning(self):
        assert self.client._map_status({"typeAankondiging": "GUNNING"}) == "gunning"

    def test_award(self):
        assert self.client._map_status({"announcementType": "CONTRACT_AWARD"}) == "gunning"

    def test_rectificatie(self):
        assert self.client._map_status({"typeAankondiging": "RECTIFICATIE"}) == "rectificatie"

    def test_corrigendum(self):
        assert self.client._map_status({"announcementType": "CORRIGENDUM"}) == "rectificatie"

    def test_vooraankondiging(self):
        assert self.client._map_status({"typeAankondiging": "VOORAANKONDIGING"}) == "vooraankondiging"

    def test_pin(self):
        assert self.client._map_status({"announcementType": "PIN"}) == "vooraankondiging"

    def test_ef25(self):
        assert self.client._map_status({"typeAankondiging": "EF25"}) == "ef25"

    def test_ef25_vrijwillige(self):
        assert self.client._map_status({"typeAankondiging": "VRIJWILLIGE_MELDING"}) == "ef25"

    def test_status_veld_fallback(self):
        assert self.client._map_status({"status": "gunning"}) == "gunning"


# ─────────────────────────────────────────────────────────────────
# Tests: TenderNedClient – _normaliseer
# ─────────────────────────────────────────────────────────────────

class TestNormaliseer:
    def setup_method(self):
        self.client = TenderNedClient(demo_mode=True)

    def test_basis_normalisatie(self):
        item = {
            "publicatiecode": "2024-123456",
            "naam": "Test aanbesteding",
            "aanbestedendeDienst": "Gemeente Test",
            "type": "europees",
            "typeAankondiging": "AANKONDIGING",
            "publicatiedatum": "2024-01-15",
        }
        result = self.client._normaliseer(item, ["72230000"])
        assert result["publicatiecode"] == "2024-123456"
        assert result["naam"] == "Test aanbesteding"
        assert result["aanbestedende_dienst"] == "Gemeente Test"
        assert result["type"] == "europees"
        assert result["cpv_codes"] == ["72230000"]

    def test_url_generatie_als_geen_url(self):
        item = {"publicatiecode": "2024-999"}
        result = self.client._normaliseer(item, [])
        assert "2024-999" in result["url_tenderned"]

    def test_cpv_omschrijvingen_uit_classificaties(self):
        item = {
            "publicatiecode": "TEST",
            "cpvCodes": [{"code": "48100000", "description": "Sectorgebonden software"}],
        }
        result = self.client._normaliseer(item, ["48100000"])
        assert "Sectorgebonden software" in result["cpv_omschrijvingen"]

    def test_waarde_uit_geschattwaarde(self):
        item = {"publicatiecode": "TEST", "geschatteWaarde": 500000.0}
        result = self.client._normaliseer(item, [])
        assert result["waarde_geschat"] == 500000.0

    def test_lege_item_geeft_defaults(self):
        result = self.client._normaliseer({}, [])
        assert result["publicatiecode"] == ""
        assert result["naam"] == ""
        assert result["cpv_codes"] == []


# ─────────────────────────────────────────────────────────────────
# Tests: TenderNedClient – live API via mocks
# ─────────────────────────────────────────────────────────────────

class TestTenderNedClientLive:
    def test_haal_van_api_succes(self, client_live):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": [
                {
                    "id": "2024-TEST01",
                    "publicatiecode": "2024-TEST01",
                    "naam": "Test ICT Aanbesteding",
                    "aanbestedendeDienst": "Gemeente Teststad",
                    "type": "Europees",
                    "typeAankondiging": "AANKONDIGING",
                    "publicatiedatum": "2024-01-10",
                    "cpvCodes": ["48100000"],
                }
            ],
            "last": True,
        }
        mock_response.raise_for_status = MagicMock()

        with patch("requests.get", return_value=mock_response):
            resultaten = client_live.haal_ict_aanbestedingen_op()

        assert len(resultaten) == 1
        assert resultaten[0]["publicatiecode"] == "2024-TEST01"

    def test_haal_van_api_filtert_niet_ict(self, client_live):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": [
                {
                    "id": "2024-BOUW01",
                    "naam": "Wegenbouw aanbesteding",
                    "cpvCodes": ["45233120"],  # Wegenbouw CPV, geen ICT
                }
            ],
            "last": True,
        }
        mock_response.raise_for_status = MagicMock()

        with patch("requests.get", return_value=mock_response):
            resultaten = client_live.haal_ict_aanbestedingen_op()

        assert len(resultaten) == 0

    def test_haal_van_api_leeg_antwoord(self, client_live):
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": [], "last": True}
        mock_response.raise_for_status = MagicMock()

        with patch("requests.get", return_value=mock_response):
            resultaten = client_live.haal_ict_aanbestedingen_op()

        assert resultaten == []

    def test_haal_van_api_request_fout(self, client_live):
        import requests as req_lib
        with patch("requests.get", side_effect=req_lib.RequestException("Timeout")):
            resultaten = client_live.haal_ict_aanbestedingen_op()

        assert resultaten == []

    def test_haal_van_api_paginering(self, client_live):
        """Test dat paginering correct stopt bij last=True."""
        call_count = 0

        def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            if call_count == 1:
                mock_resp.json.return_value = {
                    "content": [
                        {"id": f"TEST-{i}", "publicatiecode": f"TEST-{i}",
                         "naam": "ICT test", "cpvCodes": ["48000000"],
                         "publicatiedatum": "2024-01-01"}
                        for i in range(25)
                    ],
                    "last": False,
                    "totalElements": 30,
                }
            else:
                mock_resp.json.return_value = {
                    "content": [
                        {"id": "TEST-99", "publicatiecode": "TEST-99",
                         "naam": "ICT test 2", "cpvCodes": ["48000000"],
                         "publicatiedatum": "2024-01-01"}
                    ],
                    "last": True,
                }
            return mock_resp

        with patch("requests.get", side_effect=mock_get):
            resultaten = client_live.haal_ict_aanbestedingen_op(max_resultaten=100)

        assert call_count == 2
        assert len(resultaten) == 26

    def test_haal_detail_succes(self, client_live):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "TEST-DETAIL",
            "cpvCodes": ["48100000"],
        }
        mock_response.raise_for_status = MagicMock()

        with patch("requests.get", return_value=mock_response):
            result = client_live._haal_detail("TEST-DETAIL", {"fallback": True})

        assert result["id"] == "TEST-DETAIL"

    def test_haal_detail_fout_geeft_fallback(self, client_live):
        import requests as req_lib
        fallback = {"fallback": True}

        with patch("requests.get", side_effect=req_lib.RequestException("404")):
            result = client_live._haal_detail("NIET-BESTAAND", fallback)

        assert result == fallback

    def test_haal_van_api_embedded_structuur(self, client_live):
        """Test papi _embedded structuur."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "_embedded": {
                "publicaties": [
                    {
                        "id": "2024-EMB01",
                        "naam": "Embedded ICT test",
                        "cpvCodes": ["72000000"],
                        "publicatiedatum": "2024-01-15",
                    }
                ]
            },
            "last": True,
        }
        mock_response.raise_for_status = MagicMock()

        with patch("requests.get", return_value=mock_response):
            resultaten = client_live.haal_ict_aanbestedingen_op()

        assert len(resultaten) == 1

    def test_haal_van_api_detail_fallback_voor_lege_cpv(self, client_live):
        """Als lijst-item geen CPV heeft, wordt detail opgehaald."""
        list_resp = MagicMock()
        list_resp.raise_for_status = MagicMock()
        list_resp.json.return_value = {
            "content": [{"id": "DETAIL-NODIG", "naam": "Test"}],
            "last": True,
        }

        detail_resp = MagicMock()
        detail_resp.raise_for_status = MagicMock()
        detail_resp.json.return_value = {
            "id": "DETAIL-NODIG",
            "naam": "Test",
            "cpvCodes": ["48000000"],
            "publicatiedatum": "2024-01-01",
        }

        responses = [list_resp, detail_resp]
        with patch("requests.get", side_effect=responses):
            resultaten = client_live.haal_ict_aanbestedingen_op()

        assert len(resultaten) == 1


# ─────────────────────────────────────────────────────────────────
# Tests: sync_tenderned Celery task
# ─────────────────────────────────────────────────────────────────

class TestSyncTenderned:
    def test_sync_maakt_aanbestedingen_aan(self, db):
        from apps.aanbestedingen.tasks import sync_tenderned

        demo_data = [
            {
                "publicatiecode": "SYNC-001",
                "naam": "Sync Test Aanbesteding",
                "aanbestedende_dienst": "Gemeente Synctest",
                "aanbestedende_dienst_stad": "Syncstad",
                "type": "europees",
                "status": "aankondiging",
                "publicatiedatum": date.today().isoformat(),
                "cpv_codes": ["48100000"],
                "cpv_omschrijvingen": ["Software"],
                "url_tenderned": "https://tenderned.nl/SYNC-001",
            }
        ]

        with patch("apps.aanbestedingen.client.TenderNedClient") as MockClient:
            MockClient.return_value.haal_ict_aanbestedingen_op.return_value = demo_data
            result = sync_tenderned()

        assert result["aangemaakt"] == 1
        assert result["fouten"] == 0
        assert Aanbesteding.objects.filter(publicatiecode="SYNC-001").exists()

    def test_sync_werkt_bestaande_bij(self, db, aanbesteding):
        from apps.aanbestedingen.tasks import sync_tenderned

        demo_data = [
            {
                "publicatiecode": "TEST-001",  # Zelfde als fixture
                "naam": "Gewijzigde Naam",
                "aanbestedende_dienst": "Gemeente Utrecht",
                "aanbestedende_dienst_stad": "Utrecht",
                "type": "europees",
                "status": "gunning",
                "publicatiedatum": date.today().isoformat(),
                "cpv_codes": ["48100000"],
                "cpv_omschrijvingen": [],
                "url_tenderned": "https://tenderned.nl/TEST-001",
            }
        ]

        with patch("apps.aanbestedingen.client.TenderNedClient") as MockClient:
            MockClient.return_value.haal_ict_aanbestedingen_op.return_value = demo_data
            result = sync_tenderned()

        assert result["bijgewerkt"] == 1
        assert result["aangemaakt"] == 0
        aanbesteding.refresh_from_db()
        assert aanbesteding.naam == "Gewijzigde Naam"

    def test_sync_telt_fouten(self, db):
        from apps.aanbestedingen.tasks import sync_tenderned

        # Geen publicatiecode → verwerking faalt
        demo_data = [{"naam": "Ongeldige aanbesteding"}]

        with patch("apps.aanbestedingen.client.TenderNedClient") as MockClient:
            MockClient.return_value.haal_ict_aanbestedingen_op.return_value = demo_data
            result = sync_tenderned()

        assert result["fouten"] == 1

    def test_sync_herprobeert_bij_api_fout(self, db):
        from apps.aanbestedingen.tasks import sync_tenderned
        import requests as req_lib

        with patch("apps.aanbestedingen.client.TenderNedClient") as MockClient:
            MockClient.return_value.haal_ict_aanbestedingen_op.side_effect = (
                req_lib.RequestException("Timeout")
            )
            with pytest.raises(Exception):  # Celery retry raises
                sync_tenderned()

    def test_sync_koppelt_organisatie(self, db, gemeente):
        """Aanbesteding wordt gekoppeld aan bestaande organisatie."""
        from apps.aanbestedingen.tasks import sync_tenderned

        demo_data = [
            {
                "publicatiecode": "ORG-KOPPEL-001",
                "naam": "Organisatie koppeling test",
                "aanbestedende_dienst": "Gemeente Utrecht",  # Matcht gemeente fixture
                "aanbestedende_dienst_stad": "Utrecht",
                "type": "europees",
                "status": "aankondiging",
                "publicatiedatum": date.today().isoformat(),
                "cpv_codes": ["48100000"],
                "cpv_omschrijvingen": [],
                "url_tenderned": "https://tenderned.nl/ORG-KOPPEL-001",
            }
        ]

        with patch("apps.aanbestedingen.client.TenderNedClient") as MockClient:
            MockClient.return_value.haal_ict_aanbestedingen_op.return_value = demo_data
            sync_tenderned()

        aanbesteding = Aanbesteding.objects.get(publicatiecode="ORG-KOPPEL-001")
        assert aanbesteding.organisatie == gemeente


# ─────────────────────────────────────────────────────────────────
# Tests: Aanbesteding model
# ─────────────────────────────────────────────────────────────────

class TestAanbestedingModel:
    def test_primaire_cpv(self, aanbesteding):
        assert aanbesteding.primaire_cpv == "72230000"

    def test_primaire_cpv_leeg(self, db):
        a = Aanbesteding.objects.create(
            publicatiecode="LEEG-001",
            naam="Geen CPV",
            aanbestedende_dienst="Test",
            publicatiedatum=date.today(),
            url_tenderned="https://tenderned.nl/LEEG-001",
            cpv_codes=[],
        )
        assert a.primaire_cpv is None

    def test_is_ict_aanbesteding_positief(self, aanbesteding):
        assert aanbesteding.is_ict_aanbesteding

    def test_is_ict_aanbesteding_negatief(self, db):
        a = Aanbesteding.objects.create(
            publicatiecode="NIET-ICT-001",
            naam="Wegenbouw",
            aanbestedende_dienst="Test",
            publicatiedatum=date.today(),
            url_tenderned="https://tenderned.nl/NIET-ICT-001",
            cpv_codes=["45233120"],
        )
        assert not a.is_ict_aanbesteding

    def test_str_representatie(self, aanbesteding):
        str_repr = str(aanbesteding)
        assert "TEST-001" in str_repr
        assert "Test Zaaksysteem" in str_repr

    def test_status_ef25(self, db):
        a = Aanbesteding.objects.create(
            publicatiecode="EF25-001",
            naam="EF25 test",
            aanbestedende_dienst="Test",
            publicatiedatum=date.today(),
            url_tenderned="https://tenderned.nl/EF25-001",
            status=Aanbesteding.Status.EF25,
        )
        assert a.status == "ef25"


# ─────────────────────────────────────────────────────────────────
# Tests: Aanbestedingen API endpoint
# ─────────────────────────────────────────────────────────────────

class TestAanbestedingenAPI:
    def test_lijst_aanbestedingen(self, api_client, aanbesteding):
        from django.urls import reverse
        url = reverse("api:aanbesteding-list")
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] >= 1

    def test_aanbesteding_detail(self, api_client, aanbesteding):
        from django.urls import reverse
        url = reverse("api:aanbesteding-detail", kwargs={"pk": aanbesteding.pk})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["publicatiecode"] == "TEST-001"

    def test_filteren_op_status(self, api_client, db):
        from django.urls import reverse
        Aanbesteding.objects.create(
            publicatiecode="GUNNING-001",
            naam="Gegunde aanbesteding",
            aanbestedende_dienst="Test",
            publicatiedatum=date.today(),
            url_tenderned="https://tenderned.nl/GUNNING-001",
            status="gunning",
        )
        Aanbesteding.objects.create(
            publicatiecode="AANKONDIGING-001",
            naam="Aankondiging aanbesteding",
            aanbestedende_dienst="Test",
            publicatiedatum=date.today(),
            url_tenderned="https://tenderned.nl/AANKONDIGING-001",
            status="aankondiging",
        )
        url = reverse("api:aanbesteding-list")
        response = api_client.get(url, {"status": "gunning"})
        assert response.status_code == 200
        statussen = [r["status"] for r in response.data["results"]]
        assert all(s == "gunning" for s in statussen)

    def test_recente_aanbestedingen_endpoint(self, api_client, aanbesteding):
        from django.urls import reverse
        url = reverse("api:aanbesteding-list")
        response = api_client.get(url, {"limit": 5})
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────────
# Productie-modus configuratie (issue #14)
# ─────────────────────────────────────────────────────────────────

class TestProductieModus:
    """Controleert dat de client correct schakelt tussen demo- en live-modus."""

    def test_demo_mode_standaard_in_development(self):
        """In development-instellingen is demo_mode True (veilige standaard)."""
        with override_settings(TENDERNED_DEMO_MODE=True):
            client = TenderNedClient()
            assert client.demo_mode is True

    def test_live_mode_via_settings(self):
        """Met TENDERNED_DEMO_MODE=False schakelt de client naar live-modus."""
        with override_settings(TENDERNED_DEMO_MODE=False):
            client = TenderNedClient()
            assert client.demo_mode is False

    def test_expliciete_demo_mode_parameter_heeft_voorrang(self):
        """Expliciete demo_mode=True overschrijft settings."""
        with override_settings(TENDERNED_DEMO_MODE=False):
            client = TenderNedClient(demo_mode=True)
            assert client.demo_mode is True

    def test_productie_api_url_correct(self):
        """In productie-modus gebruikt de client de juiste TenderNed papi URL."""
        verwachte_url = "https://www.tenderned.nl/papi/tenderned-rs-tns/v2/publicaties"
        with override_settings(TENDERNED_DEMO_MODE=False, TENDERNED_API_URL=verwachte_url):
            client = TenderNedClient()
            assert client.base_url == verwachte_url

    def test_timeout_configureerbaar(self):
        """Timeout is configureerbaar via TENDERNED_TIMEOUT setting."""
        with override_settings(TENDERNED_TIMEOUT=60):
            client = TenderNedClient()
            assert client.timeout == 60

    @patch("apps.aanbestedingen.client.requests.get")
    def test_live_modus_roept_echte_api_aan(self, mock_get):
        """In live-modus wordt de echte TenderNed API aangeroepen (niet demo-data)."""
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"content": [], "last": True},
        )
        with override_settings(TENDERNED_DEMO_MODE=False):
            client = TenderNedClient(
                demo_mode=False,
                base_url="https://mock.tenderned.nl/api",
            )
            client.haal_ict_aanbestedingen_op(dagen_terug=1, max_resultaten=5)

        assert mock_get.called, "requests.get moet aangeroepen zijn in live-modus"

    def test_demo_modus_roept_geen_api_aan(self):
        """In demo-modus worden geen HTTP-verzoeken gedaan."""
        with patch("apps.aanbestedingen.client.requests.get") as mock_get:
            client = TenderNedClient(demo_mode=True)
            resultaten = client.haal_ict_aanbestedingen_op(dagen_terug=7, max_resultaten=10)
            assert not mock_get.called, "requests.get mag NIET aangeroepen worden in demo-modus"
            assert len(resultaten) > 0, "Demo-modus moet voorbeelddata teruggeven"

    def test_productie_settings_override_base(self):
        """Productie-instellingen: TENDERNED_DEMO_MODE standaard False."""
        # Simuleer productie-instellingen
        with override_settings(TENDERNED_DEMO_MODE=False, TENDERNED_TIMEOUT=60):
            client = TenderNedClient()
            assert client.demo_mode is False
            assert client.timeout == 60
