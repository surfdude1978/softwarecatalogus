"""Tests voor zoek- en export-views."""
from unittest.mock import patch

import pytest
from django.urls import reverse

from apps.pakketten.models import Pakket

pytestmark = pytest.mark.django_db


# ─────────────────────────────────────────────────────────────────
# Tests: ZoekView (Meilisearch)
# ─────────────────────────────────────────────────────────────────

class TestZoekView:
    """Tests voor /api/v1/zoeken/ endpoint (Meilisearch-backed)."""

    def _mock_search_result(self, hits=None):
        return {
            "hits": hits or [],
            "totalHits": len(hits or []),
            "offset": 0,
            "limit": 25,
        }

    def test_zoeken_zonder_query_geeft_400(self, api_client):
        url = reverse("api:zoek")
        response = api_client.get(url)
        assert response.status_code == 400
        assert "q" in response.data["detail"].lower() or "zoekterm" in response.data["detail"].lower()

    def test_zoeken_met_query_geeft_resultaten(self, api_client):
        mock_result = self._mock_search_result([
            {"id": "1", "naam": "Suite4Gemeenten", "status": "actief"}
        ])
        with patch("apps.api.search_views.search_pakketten", return_value=mock_result):
            url = reverse("api:zoek")
            response = api_client.get(url, {"q": "Suite"})

        assert response.status_code == 200
        assert response.data["totalHits"] == 1

    def test_zoeken_lege_resultaten(self, api_client):
        mock_result = self._mock_search_result([])
        with patch("apps.api.search_views.search_pakketten", return_value=mock_result):
            url = reverse("api:zoek")
            response = api_client.get(url, {"q": "onbestaandpakket"})

        assert response.status_code == 200
        assert response.data["totalHits"] == 0

    def test_zoeken_met_licentievorm_filter(self, api_client):
        mock_result = self._mock_search_result()
        with patch("apps.api.search_views.search_pakketten", return_value=mock_result) as mock_fn:
            url = reverse("api:zoek")
            api_client.get(url, {"q": "test", "licentievorm": "saas"})

        # Controleer dat de filter doorgegeven is
        call_args = mock_fn.call_args
        assert 'saas' in call_args.kwargs.get("filters", "") or \
               (call_args.args and 'saas' in str(call_args.args))

    def test_zoeken_met_leverancier_filter(self, api_client, leverancier):
        mock_result = self._mock_search_result()
        with patch("apps.api.search_views.search_pakketten", return_value=mock_result) as mock_fn:
            url = reverse("api:zoek")
            api_client.get(url, {"q": "test", "leverancier": str(leverancier.pk)})

        call_args = mock_fn.call_args
        assert str(leverancier.pk) in call_args.kwargs.get("filters", "") or \
               (call_args.args and str(leverancier.pk) in str(call_args.args))

    def test_zoeken_met_standaard_filter(self, api_client, standaard):
        mock_result = self._mock_search_result()
        with patch("apps.api.search_views.search_pakketten", return_value=mock_result) as mock_fn:
            url = reverse("api:zoek")
            api_client.get(url, {"q": "test", "standaard": str(standaard.pk)})

        call_args = mock_fn.call_args
        assert str(standaard.pk) in call_args.kwargs.get("filters", "") or \
               (call_args.args and str(standaard.pk) in str(call_args.args))

    def test_zoeken_met_gemma_component_filter(self, api_client, gemma_component):
        mock_result = self._mock_search_result()
        with patch("apps.api.search_views.search_pakketten", return_value=mock_result) as mock_fn:
            url = reverse("api:zoek")
            api_client.get(url, {"q": "test", "gemma_component": str(gemma_component.pk)})

        call_args = mock_fn.call_args
        assert str(gemma_component.pk) in call_args.kwargs.get("filters", "") or \
               (call_args.args and str(gemma_component.pk) in str(call_args.args))

    def test_zoeken_met_sort_naam_asc(self, api_client):
        mock_result = self._mock_search_result()
        with patch("apps.api.search_views.search_pakketten", return_value=mock_result) as mock_fn:
            url = reverse("api:zoek")
            api_client.get(url, {"q": "test", "sort": "naam:asc"})

        call_args = mock_fn.call_args
        sort = call_args.kwargs.get("sort") or (call_args.args[2] if len(call_args.args) > 2 else None)
        assert sort == ["naam:asc"]

    def test_zoeken_met_paginatie(self, api_client):
        mock_result = self._mock_search_result()
        with patch("apps.api.search_views.search_pakketten", return_value=mock_result) as mock_fn:
            url = reverse("api:zoek")
            api_client.get(url, {"q": "test", "offset": "10", "limit": "5"})

        call_args = mock_fn.call_args
        assert call_args.kwargs.get("offset") == 10 or \
               (call_args.args and 10 in call_args.args)
        assert call_args.kwargs.get("limit") == 5 or \
               (call_args.args and 5 in call_args.args)

    def test_zoeken_ongeldige_paginatie_gebruikt_defaults(self, api_client):
        mock_result = self._mock_search_result()
        with patch("apps.api.search_views.search_pakketten", return_value=mock_result) as mock_fn:
            url = reverse("api:zoek")
            api_client.get(url, {"q": "test", "offset": "abc", "limit": "xyz"})

        call_args = mock_fn.call_args
        # Defaults: offset=0, limit=25
        assert call_args.kwargs.get("offset", 0) == 0
        assert call_args.kwargs.get("limit", 25) == 25

    def test_zoeken_limit_max_100(self, api_client):
        mock_result = self._mock_search_result()
        with patch("apps.api.search_views.search_pakketten", return_value=mock_result) as mock_fn:
            url = reverse("api:zoek")
            api_client.get(url, {"q": "test", "limit": "9999"})

        call_args = mock_fn.call_args
        limit = call_args.kwargs.get("limit")
        assert limit <= 100

    def test_zoeken_ongeldige_sort_wordt_genegeerd(self, api_client):
        mock_result = self._mock_search_result()
        with patch("apps.api.search_views.search_pakketten", return_value=mock_result) as mock_fn:
            url = reverse("api:zoek")
            api_client.get(url, {"q": "test", "sort": "invalid_sort"})

        call_args = mock_fn.call_args
        sort = call_args.kwargs.get("sort")
        assert sort is None


# ─────────────────────────────────────────────────────────────────
# Tests: Export views – pakketten
# ─────────────────────────────────────────────────────────────────

class TestExportPakkettenCSV:
    def test_export_pakketten_csv_succes(self, api_client, pakket):
        url = reverse("api:export-pakketten-csv")
        response = api_client.get(url)
        assert response.status_code == 200
        assert "text/csv" in response["Content-Type"]
        content = response.content.decode("utf-8-sig")
        assert "Suite4Gemeenten" in content

    def test_export_csv_bevat_header(self, api_client):
        url = reverse("api:export-pakketten-csv")
        response = api_client.get(url)
        content = response.content.decode("utf-8-sig")
        assert "Naam" in content
        assert "Leverancier" in content

    def test_export_csv_bevat_bom(self, api_client):
        url = reverse("api:export-pakketten-csv")
        response = api_client.get(url)
        # BOM voor Excel: \xef\xbb\xbf
        assert response.content[:3] == b"\xef\xbb\xbf"

    def test_export_csv_heeft_juiste_content_disposition(self, api_client):
        url = reverse("api:export-pakketten-csv")
        response = api_client.get(url)
        assert "attachment" in response["Content-Disposition"]
        assert ".csv" in response["Content-Disposition"]

    def test_export_csv_sluit_verouderde_pakketten_uit(self, api_client, db, leverancier):
        Pakket.objects.create(
            naam="OudPakketExport",
            status=Pakket.Status.VEROUDERD,
            leverancier=leverancier,
        )
        url = reverse("api:export-pakketten-csv")
        response = api_client.get(url)
        content = response.content.decode("utf-8-sig")
        assert "OudPakketExport" not in content


class TestExportPakkettenExcel:
    def test_export_pakketten_excel_succes(self, api_client, pakket):
        url = reverse("api:export-pakketten-xlsx")
        response = api_client.get(url)
        assert response.status_code == 200
        content_type = response["Content-Type"]
        assert "openxmlformats" in content_type or "spreadsheetml" in content_type

    def test_export_excel_heeft_juiste_content_disposition(self, api_client):
        url = reverse("api:export-pakketten-xlsx")
        response = api_client.get(url)
        assert "attachment" in response["Content-Disposition"]
        assert ".xlsx" in response["Content-Disposition"]

    def test_export_excel_geeft_binaire_data(self, api_client):
        url = reverse("api:export-pakketten-xlsx")
        response = api_client.get(url)
        # XLSX begint met PK (ZIP)
        assert response.content[:2] == b"PK"


# ─────────────────────────────────────────────────────────────────
# Tests: Export views – pakketoverzicht (authenticatie vereist)
# ─────────────────────────────────────────────────────────────────

class TestExportPakketOverzicht:
    def test_export_overzicht_csv_vereist_auth(self, api_client):
        url = reverse("api:export-overzicht-csv")
        response = api_client.get(url)
        assert response.status_code == 401

    def test_export_overzicht_excel_vereist_auth(self, api_client):
        url = reverse("api:export-overzicht-xlsx")
        response = api_client.get(url)
        assert response.status_code == 401

    def test_export_overzicht_ameff_vereist_auth(self, api_client):
        url = reverse("api:export-overzicht-ameff")
        response = api_client.get(url)
        assert response.status_code == 401

    def test_export_overzicht_csv_zonder_organisatie(self, api_client, functioneel_beheerder):
        from rest_framework_simplejwt.tokens import RefreshToken
        # Functioneel beheerder heeft geen organisatie
        refresh = RefreshToken.for_user(functioneel_beheerder)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        url = reverse("api:export-overzicht-csv")
        response = api_client.get(url)
        assert response.status_code == 400

    def test_export_overzicht_csv_succes(self, auth_client, pakket_gebruik):
        url = reverse("api:export-overzicht-csv")
        response = auth_client.get(url)
        assert response.status_code == 200
        assert "text/csv" in response["Content-Type"]

    def test_export_overzicht_csv_bevat_pakket(self, auth_client, pakket_gebruik):
        url = reverse("api:export-overzicht-csv")
        response = auth_client.get(url)
        content = response.content.decode("utf-8-sig")
        assert "Suite4Gemeenten" in content

    def test_export_overzicht_excel_succes(self, auth_client, pakket_gebruik):
        url = reverse("api:export-overzicht-xlsx")
        response = auth_client.get(url)
        assert response.status_code == 200
        # XLSX begint met PK
        assert response.content[:2] == b"PK"

    def test_export_overzicht_excel_zonder_organisatie(self, api_client, functioneel_beheerder):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(functioneel_beheerder)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        url = reverse("api:export-overzicht-xlsx")
        response = api_client.get(url)
        assert response.status_code == 400

    def test_export_overzicht_ameff_succes(self, auth_client, pakket_gebruik):
        url = reverse("api:export-overzicht-ameff")
        response = auth_client.get(url)
        assert response.status_code == 200
        assert "xml" in response["Content-Type"]

    def test_export_overzicht_ameff_zonder_organisatie(self, api_client, functioneel_beheerder):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(functioneel_beheerder)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        url = reverse("api:export-overzicht-ameff")
        response = api_client.get(url)
        assert response.status_code == 400
