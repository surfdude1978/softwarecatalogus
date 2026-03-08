"""Tests voor audit logging (issue #8/#16)."""
import pytest
from django.urls import reverse
from unittest.mock import patch

from apps.core.audit import AuditLog, log_actie, _get_ip, _get_object_info


pytestmark = pytest.mark.django_db


# ─────────────────────────────────────────────────────────────────
# Tests: AuditLog model
# ─────────────────────────────────────────────────────────────────

class TestAuditLogModel:
    def test_str_methode(self, db):
        entry = AuditLog.objects.create(
            actor_email="test@example.com",
            actie=AuditLog.Actie.AANGEMAAKT,
            object_type="Pakket",
            object_id="abc-123",
            object_omschrijving="Suite4Gemeenten",
        )
        assert "test@example.com" in str(entry)
        assert "aangemaakt" in str(entry)

    def test_str_anoniem(self, db):
        entry = AuditLog.objects.create(
            actie=AuditLog.Actie.AANGEMAAKT,
            object_type="Pakket",
        )
        assert "anoniem" in str(entry)

    def test_tijdstip_auto_gezet(self, db):
        entry = AuditLog.objects.create(
            actie=AuditLog.Actie.AANGEMAAKT,
            object_type="Pakket",
        )
        assert entry.tijdstip is not None

    def test_ordering_nieuwste_eerst(self, db):
        for i in range(3):
            AuditLog.objects.create(actie=AuditLog.Actie.AANGEMAAKT, object_type="Test")
        entries = list(AuditLog.objects.all())
        # Nieuwste bovenaan
        assert entries[0].pk > entries[-1].pk

    def test_alle_actie_waarden_geldig(self, db):
        for actie in AuditLog.Actie.values:
            entry = AuditLog.objects.create(actie=actie, object_type="Test")
            assert entry.actie == actie


# ─────────────────────────────────────────────────────────────────
# Tests: log_actie() helper
# ─────────────────────────────────────────────────────────────────

class TestLogActie:
    def _make_anon_request(self, extra_meta=None):
        """Maak een anonieme MagicMock request aan."""
        from unittest.mock import MagicMock
        req = MagicMock()
        anon = MagicMock()
        anon.is_authenticated = False
        req.user = anon
        req.META = {"REMOTE_ADDR": "127.0.0.1", "HTTP_USER_AGENT": "pytest"}
        if extra_meta:
            req.META.update(extra_meta)
        return req

    def _make_user_request(self, user):
        """Maak een MagicMock request met een echte gebruiker."""
        from unittest.mock import MagicMock
        req = MagicMock()
        req.user = user
        req.META = {"REMOTE_ADDR": "127.0.0.1", "HTTP_USER_AGENT": "pytest"}
        return req

    def test_log_actie_met_instance(self, db, pakket):
        req = self._make_anon_request()
        entry = log_actie(req, AuditLog.Actie.AANGEMAAKT, instance=pakket)
        assert entry.object_type == "Pakket"
        assert entry.object_id == str(pakket.pk)
        assert entry.object_omschrijving == pakket.naam

    def test_log_actie_met_actor(self, db, gebruik_beheerder, pakket):
        req = self._make_user_request(gebruik_beheerder)
        req.META["REMOTE_ADDR"] = "10.0.0.1"
        entry = log_actie(req, AuditLog.Actie.BIJGEWERKT, instance=pakket)
        assert entry.actor_id == str(gebruik_beheerder.pk)
        assert entry.actor_email == gebruik_beheerder.email

    def test_log_actie_ip_adres(self, db, pakket):
        req = self._make_anon_request({"REMOTE_ADDR": "192.168.1.1"})
        entry = log_actie(req, AuditLog.Actie.AANGEMAAKT, instance=pakket)
        assert entry.ip_adres == "192.168.1.1"

    def test_log_actie_x_forwarded_for(self, db, pakket):
        req = self._make_anon_request({
            "HTTP_X_FORWARDED_FOR": "203.0.113.1, 10.0.0.1",
            "REMOTE_ADDR": "10.0.0.2",
        })
        entry = log_actie(req, AuditLog.Actie.AANGEMAAKT, instance=pakket)
        assert entry.ip_adres == "203.0.113.1"

    def test_log_actie_met_wijzigingen(self, db, pakket):
        req = self._make_anon_request()
        wijzigingen = {"naam": {"oud": "Oud", "nieuw": "Nieuw"}}
        entry = log_actie(
            req, AuditLog.Actie.BIJGEWERKT, instance=pakket, wijzigingen=wijzigingen
        )
        assert entry.wijzigingen == wijzigingen

    def test_log_actie_zonder_instance(self, db):
        req = self._make_anon_request()
        entry = log_actie(
            req,
            AuditLog.Actie.EXPORT,
            object_type="PakketOverzicht",
            object_id="uuid-123",
            object_omschrijving="Gemeente Test",
        )
        assert entry.object_type == "PakketOverzicht"
        assert entry.object_id == "uuid-123"


# ─────────────────────────────────────────────────────────────────
# Tests: AuditLogMixin via API (integratie)
# ─────────────────────────────────────────────────────────────────

class TestAuditLogMixinIntegratie:
    def test_aanmaken_pakket_logt_actie(self, api_client, aanbod_beheerder, leverancier):
        """Aanmaken via API door aanbod_beheerder → AuditLog entry met actie=aangemaakt."""
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(aanbod_beheerder)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        url = reverse("api:pakket-list")
        voor = AuditLog.objects.count()
        api_client.post(url, {
            "naam": "Nieuw Pakket",
            "leverancier": str(leverancier.pk),
            "status": "concept",
            "licentievorm": "saas",
        })
        assert AuditLog.objects.count() > voor
        entry = AuditLog.objects.filter(actie=AuditLog.Actie.AANGEMAAKT).last()
        assert entry is not None
        assert entry.object_type == "Pakket"

    def test_verwijderen_pakketgebruik_logt_actie(self, auth_client, pakket_gebruik):
        """Verwijderen via API → AuditLog entry met actie=verwijderd."""
        url = reverse("api:mijn-pakketoverzicht-detail", args=[str(pakket_gebruik.pk)])
        voor = AuditLog.objects.filter(actie=AuditLog.Actie.VERWIJDERD).count()
        auth_client.delete(url)
        assert AuditLog.objects.filter(actie=AuditLog.Actie.VERWIJDERD).count() > voor


# ─────────────────────────────────────────────────────────────────
# Tests: ExportAuditLogCSV
# ─────────────────────────────────────────────────────────────────

class TestExportAuditLogCSV:
    def _fb_client(self, api_client, functioneel_beheerder):
        """Geef een api_client met functioneel beheerder token."""
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(functioneel_beheerder)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return api_client

    def test_export_vereist_auth(self, api_client):
        url = reverse("api:export-auditlog-csv")
        response = api_client.get(url)
        assert response.status_code in (401, 403)

    def test_export_vereist_functioneel_beheerder(self, auth_client):
        """Gebruik-beheerder (geen functioneel) heeft geen toegang."""
        url = reverse("api:export-auditlog-csv")
        response = auth_client.get(url)
        assert response.status_code == 403

    def test_export_succes_functioneel_beheerder(self, api_client, functioneel_beheerder, db):
        fb_client = self._fb_client(api_client, functioneel_beheerder)
        # Maak een log entry aan
        AuditLog.objects.create(
            actor_email="test@test.nl",
            actie=AuditLog.Actie.AANGEMAAKT,
            object_type="Pakket",
            object_omschrijving="TestPakket",
        )
        url = reverse("api:export-auditlog-csv")
        response = fb_client.get(url)
        assert response.status_code == 200
        assert "text/csv" in response["Content-Type"]

    def test_export_bevat_bom(self, api_client, functioneel_beheerder, db):
        fb_client = self._fb_client(api_client, functioneel_beheerder)
        url = reverse("api:export-auditlog-csv")
        response = fb_client.get(url)
        assert response.content[:3] == b"\xef\xbb\xbf"

    def test_export_heeft_header_rij(self, api_client, functioneel_beheerder, db):
        fb_client = self._fb_client(api_client, functioneel_beheerder)
        url = reverse("api:export-auditlog-csv")
        response = fb_client.get(url)
        content = response.content.decode("utf-8-sig")
        assert "Tijdstip" in content
        assert "Actor e-mail" in content
        assert "Actie" in content

    def test_export_bevat_log_entry(self, api_client, functioneel_beheerder, db):
        fb_client = self._fb_client(api_client, functioneel_beheerder)
        AuditLog.objects.create(
            actor_email="beheerder@gemeente.nl",
            actie=AuditLog.Actie.BIJGEWERKT,
            object_type="Organisatie",
            object_omschrijving="Gemeente Utrecht",
        )
        url = reverse("api:export-auditlog-csv")
        response = fb_client.get(url)
        content = response.content.decode("utf-8-sig")
        assert "beheerder@gemeente.nl" in content
        assert "bijgewerkt" in content

    def test_export_filter_op_actie(self, api_client, functioneel_beheerder, db):
        fb_client = self._fb_client(api_client, functioneel_beheerder)
        AuditLog.objects.create(actie=AuditLog.Actie.AANGEMAAKT, object_type="Pakket")
        AuditLog.objects.create(actie=AuditLog.Actie.VERWIJDERD, object_type="Pakket")
        url = reverse("api:export-auditlog-csv")
        response = fb_client.get(url, {"actie": "verwijderd"})
        content = response.content.decode("utf-8-sig")
        assert "verwijderd" in content
        assert "aangemaakt" not in content.replace("aangemaakt", "")  # Niet in datakolom

    def test_export_content_disposition(self, api_client, functioneel_beheerder, db):
        fb_client = self._fb_client(api_client, functioneel_beheerder)
        url = reverse("api:export-auditlog-csv")
        response = fb_client.get(url)
        assert "attachment" in response["Content-Disposition"]
        assert "auditlog" in response["Content-Disposition"]
        assert ".csv" in response["Content-Disposition"]

    def test_export_logt_zelf_ook(self, api_client, functioneel_beheerder, db):
        """De audit log export wordt zelf ook gelogd."""
        fb_client = self._fb_client(api_client, functioneel_beheerder)
        url = reverse("api:export-auditlog-csv")
        voor = AuditLog.objects.filter(actie=AuditLog.Actie.EXPORT).count()
        fb_client.get(url)
        assert AuditLog.objects.filter(actie=AuditLog.Actie.EXPORT).count() > voor
