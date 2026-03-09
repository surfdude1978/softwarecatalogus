"""Tests voor de zelfregistratie- en fiatteerstroom (issue #13)."""

import pytest
from django.urls import reverse

from apps.gebruikers.models import User

pytestmark = pytest.mark.django_db


# ── AdminGebruikerViewSet ─────────────────────────────────────────────────────


class TestAdminGebruikerWachtend:
    """GET /api/v1/admin/gebruikers/wachtend/ — lijst wachtende gebruikers."""

    def test_vereist_functioneel_beheerder(self, auth_client):
        url = reverse("api:admin-gebruiker-wachtend")
        response = auth_client.get(url)
        assert response.status_code == 403

    def test_anoniem_krijgt_401(self, api_client):
        url = reverse("api:admin-gebruiker-wachtend")
        response = api_client.get(url)
        assert response.status_code == 401

    def test_retourneert_wachtende_gebruikers(self, admin_client, wachtend_gebruiker, gebruik_beheerder):
        url = reverse("api:admin-gebruiker-wachtend")
        response = admin_client.get(url)
        assert response.status_code == 200
        ids = [g["id"] for g in response.data]
        assert str(wachtend_gebruiker.id) in ids
        # Actieve gebruik_beheerder hoort er NIET in
        assert str(gebruik_beheerder.id) not in ids

    def test_lege_lijst_als_geen_wachtenden(self, admin_client):
        url = reverse("api:admin-gebruiker-wachtend")
        response = admin_client.get(url)
        assert response.status_code == 200
        assert response.data == []


class TestAdminGebruikerFiatteren:
    """POST /api/v1/admin/gebruikers/{id}/fiatteren/ — activeer wachtende gebruiker."""

    def test_fiatteren_activeert_gebruiker(self, admin_client, wachtend_gebruiker):
        url = reverse(
            "api:admin-gebruiker-fiatteren",
            kwargs={"pk": str(wachtend_gebruiker.pk)},
        )
        response = admin_client.post(url)
        assert response.status_code == 200

        wachtend_gebruiker.refresh_from_db()
        assert wachtend_gebruiker.status == User.Status.ACTIEF

    def test_fiatteren_retourneert_gebruikersprofiel(self, admin_client, wachtend_gebruiker):
        url = reverse(
            "api:admin-gebruiker-fiatteren",
            kwargs={"pk": str(wachtend_gebruiker.pk)},
        )
        response = admin_client.post(url)
        assert response.status_code == 200
        assert response.data["email"] == wachtend_gebruiker.email
        assert response.data["status"] == "actief"

    def test_fiatteren_van_actieve_gebruiker_geeft_fout(self, admin_client, gebruik_beheerder):
        url = reverse(
            "api:admin-gebruiker-fiatteren",
            kwargs={"pk": str(gebruik_beheerder.pk)},
        )
        response = admin_client.post(url)
        assert response.status_code == 400
        assert "wachtende" in response.data["detail"].lower()

    def test_fiatteren_vereist_functioneel_beheerder(self, auth_client, wachtend_gebruiker):
        url = reverse(
            "api:admin-gebruiker-fiatteren",
            kwargs={"pk": str(wachtend_gebruiker.pk)},
        )
        response = auth_client.post(url)
        assert response.status_code == 403

    def test_fiatteren_logt_audit(self, admin_client, wachtend_gebruiker):
        from apps.core.audit import AuditLog

        url = reverse(
            "api:admin-gebruiker-fiatteren",
            kwargs={"pk": str(wachtend_gebruiker.pk)},
        )
        admin_client.post(url)
        assert AuditLog.objects.filter(
            actie=AuditLog.Actie.GEFIATEERD,
            object_type="User",
            object_id=str(wachtend_gebruiker.pk),
        ).exists()


class TestAdminGebruikerAfwijzen:
    """POST /api/v1/admin/gebruikers/{id}/afwijzen/ — wijs wachtende gebruiker af."""

    def test_afwijzen_zet_status_op_inactief(self, admin_client, wachtend_gebruiker):
        url = reverse(
            "api:admin-gebruiker-afwijzen",
            kwargs={"pk": str(wachtend_gebruiker.pk)},
        )
        response = admin_client.post(url, {"reden": "Onbekende organisatie."}, format="json")
        assert response.status_code == 200

        wachtend_gebruiker.refresh_from_db()
        assert wachtend_gebruiker.status == User.Status.INACTIEF

    def test_afwijzen_van_actieve_gebruiker_geeft_fout(self, admin_client, gebruik_beheerder):
        url = reverse(
            "api:admin-gebruiker-afwijzen",
            kwargs={"pk": str(gebruik_beheerder.pk)},
        )
        response = admin_client.post(url)
        assert response.status_code == 400

    def test_afwijzen_vereist_functioneel_beheerder(self, auth_client, wachtend_gebruiker):
        url = reverse(
            "api:admin-gebruiker-afwijzen",
            kwargs={"pk": str(wachtend_gebruiker.pk)},
        )
        response = auth_client.post(url)
        assert response.status_code == 403


# ── AdminGebruikerViewSet — list / retrieve ───────────────────────────────────


class TestAdminGebruikerLijst:
    """GET /api/v1/admin/gebruikers/ — alle gebruikers voor admin."""

    def test_admin_ziet_alle_gebruikers(self, admin_client, gebruik_beheerder, wachtend_gebruiker):
        url = reverse("api:admin-gebruiker-list")
        response = admin_client.get(url)
        assert response.status_code == 200
        ids = [g["id"] for g in response.data["results"]]
        assert str(gebruik_beheerder.id) in ids
        assert str(wachtend_gebruiker.id) in ids

    def test_filter_op_status(self, admin_client, gebruik_beheerder, wachtend_gebruiker):
        url = reverse("api:admin-gebruiker-list") + "?status=wacht_op_fiattering"
        response = admin_client.get(url)
        assert response.status_code == 200
        ids = [g["id"] for g in response.data["results"]]
        assert str(wachtend_gebruiker.id) in ids
        assert str(gebruik_beheerder.id) not in ids

    def test_niet_admin_krijgt_403(self, auth_client):
        url = reverse("api:admin-gebruiker-list")
        response = auth_client.get(url)
        assert response.status_code == 403


# ── Registratie flow ─────────────────────────────────────────────────────────


class TestRegistratieMetOrganisatie:
    """POST /api/v1/auth/registreer/ — registratie met organisatielink."""

    def test_registreer_met_bestaande_organisatie(self, api_client, gemeente):
        url = reverse("api:registreer")
        response = api_client.post(
            url,
            {
                "naam": "Nieuwe Medewerker",
                "email": "nieuw@utrecht.nl",
                "organisatie": str(gemeente.id),
                "password": "VeiligWachtwoord1!",
                "password_confirm": "VeiligWachtwoord1!",
            },
            format="json",
        )
        assert response.status_code == 201
        user = User.objects.get(email="nieuw@utrecht.nl")
        assert user.status == User.Status.WACHT_OP_FIATTERING
        assert user.organisatie == gemeente

    def test_registreer_zonder_organisatie_is_optioneel(self, api_client):
        """organisatie is optioneel in de serializer — mag None zijn."""
        url = reverse("api:registreer")
        response = api_client.post(
            url,
            {
                "naam": "Anoniem",
                "email": "anoniem@test.nl",
                "password": "VeiligWachtwoord1!",
                "password_confirm": "VeiligWachtwoord1!",
            },
            format="json",
        )
        assert response.status_code == 201
        user = User.objects.get(email="anoniem@test.nl")
        assert user.status == User.Status.WACHT_OP_FIATTERING
        assert user.organisatie is None

    def test_wachtend_gebruiker_kan_niet_inloggen(self, api_client, wachtend_gebruiker):
        """Een gebruiker in wacht_op_fiattering-status kan niet inloggen."""
        url = reverse("api:login")
        response = api_client.post(
            url,
            {
                "email": "wachtend@example.com",
                "password": "TestWachtwoord123!",
            },
            format="json",
        )
        assert response.status_code == 403
        assert "goedkeuring" in response.data["detail"].lower()

    def test_na_fiattering_kan_gebruiker_inloggen(self, api_client, admin_client, wachtend_gebruiker):
        """Na fiattering door de admin moet de gebruiker kunnen inloggen."""
        fiateer_url = reverse(
            "api:admin-gebruiker-fiatteren",
            kwargs={"pk": str(wachtend_gebruiker.pk)},
        )
        admin_client.post(fiateer_url)

        login_url = reverse("api:login")
        response = api_client.post(
            login_url,
            {
                "email": "wachtend@example.com",
                "password": "TestWachtwoord123!",
            },
            format="json",
        )
        assert response.status_code == 200
        assert "access" in response.data or response.data.get("totp_required") is False
