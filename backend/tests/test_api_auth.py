"""Tests voor authenticatie endpoints."""
import pytest
from django.urls import reverse

from apps.gebruikers.models import User


pytestmark = pytest.mark.django_db


class TestLoginAPI:
    def test_login_zonder_2fa(self, api_client, gebruik_beheerder):
        url = reverse("api:login")
        response = api_client.post(url, {
            "email": "gebruik@utrecht.nl",
            "password": "TestWachtwoord123!",
        })
        assert response.status_code == 200
        assert response.data["totp_required"] is False
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert response.data["user"]["email"] == "gebruik@utrecht.nl"

    def test_login_met_onjuist_wachtwoord(self, api_client, gebruik_beheerder):
        url = reverse("api:login")
        response = api_client.post(url, {
            "email": "gebruik@utrecht.nl",
            "password": "FoutWachtwoord",
        })
        assert response.status_code == 401
        assert "Ongeldige inloggegevens" in response.data["detail"]

    def test_login_zonder_email(self, api_client):
        url = reverse("api:login")
        response = api_client.post(url, {"password": "wachtwoord"})
        assert response.status_code == 400

    def test_login_inactieve_gebruiker(self, api_client, inactieve_gebruiker):
        url = reverse("api:login")
        response = api_client.post(url, {
            "email": "inactief@example.com",
            "password": "TestWachtwoord123!",
        })
        assert response.status_code == 403
        assert "gedeactiveerd" in response.data["detail"]

    def test_login_wachtende_gebruiker(self, api_client, wachtend_gebruiker):
        url = reverse("api:login")
        response = api_client.post(url, {
            "email": "wachtend@example.com",
            "password": "TestWachtwoord123!",
        })
        assert response.status_code == 403
        assert "goedkeuring" in response.data["detail"]

    def test_login_met_2fa_retourneert_temp_token(self, api_client, gebruik_beheerder):
        from django_otp.plugins.otp_totp.models import TOTPDevice
        gebruik_beheerder.totp_enabled = True
        gebruik_beheerder.save()
        TOTPDevice.objects.create(user=gebruik_beheerder, confirmed=True, name="test")

        url = reverse("api:login")
        response = api_client.post(url, {
            "email": "gebruik@utrecht.nl",
            "password": "TestWachtwoord123!",
        })
        assert response.status_code == 200
        assert response.data["totp_required"] is True
        assert "temp_token" in response.data
        assert "access" not in response.data


class TestRegistratieAPI:
    def test_registratie_succesvol(self, api_client, gemeente):
        url = reverse("api:registreer")
        data = {
            "email": "nieuw@test.nl",
            "naam": "Nieuwe Gebruiker",
            "password": "SterkWachtwoord123!",
            "password_confirm": "SterkWachtwoord123!",
            "organisatie": str(gemeente.pk),
        }
        response = api_client.post(url, data)
        assert response.status_code == 201
        assert "user_id" in response.data
        user = User.objects.get(email="nieuw@test.nl")
        assert user.status == User.Status.WACHT_OP_FIATTERING
        assert user.organisatie == gemeente

    def test_registratie_wachtwoorden_ongelijk(self, api_client, gemeente):
        url = reverse("api:registreer")
        data = {
            "email": "nieuw@test.nl",
            "naam": "Test",
            "password": "SterkWachtwoord123!",
            "password_confirm": "AnderWachtwoord123!",
            "organisatie": str(gemeente.pk),
        }
        response = api_client.post(url, data)
        assert response.status_code == 400

    def test_registratie_te_kort_wachtwoord(self, api_client, gemeente):
        url = reverse("api:registreer")
        data = {
            "email": "nieuw@test.nl",
            "naam": "Test",
            "password": "kort",
            "password_confirm": "kort",
            "organisatie": str(gemeente.pk),
        }
        response = api_client.post(url, data)
        assert response.status_code == 400

    def test_registratie_dubbel_email(self, api_client, gebruik_beheerder, gemeente):
        url = reverse("api:registreer")
        data = {
            "email": "gebruik@utrecht.nl",
            "naam": "Dubbel",
            "password": "SterkWachtwoord123!",
            "password_confirm": "SterkWachtwoord123!",
            "organisatie": str(gemeente.pk),
        }
        response = api_client.post(url, data)
        assert response.status_code == 400


class TestLogoutAPI:
    def test_logout(self, auth_client, gebruik_beheerder):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(gebruik_beheerder)
        url = reverse("api:logout")
        response = auth_client.post(url, {"refresh": str(refresh)})
        assert response.status_code == 200
        assert "Uitgelogd" in response.data["detail"]

    def test_logout_zonder_auth_verboden(self, api_client):
        url = reverse("api:logout")
        response = api_client.post(url)
        assert response.status_code == 401


class TestWachtwoordResetAPI:
    def test_wachtwoord_reset_request(self, api_client, gebruik_beheerder):
        url = reverse("api:wachtwoord-reset")
        response = api_client.post(url, {"email": "gebruik@utrecht.nl"})
        assert response.status_code == 200
        # Altijd succesmelding (voorkomt email enumeration)
        assert "reset-link" in response.data["detail"]

    def test_wachtwoord_reset_onbekend_email(self, api_client):
        url = reverse("api:wachtwoord-reset")
        response = api_client.post(url, {"email": "onbekend@example.com"})
        assert response.status_code == 200  # Geen foutmelding


class TestProfielAPI:
    def test_profiel_ophalen(self, auth_client, gebruik_beheerder):
        url = reverse("api:profiel-mij")
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response.data["email"] == "gebruik@utrecht.nl"
        assert response.data["naam"] == "Gebruik Beheerder"
        assert "rol" in response.data
        assert "organisatie_naam" in response.data

    def test_profiel_bijwerken(self, auth_client):
        url = reverse("api:profiel-mij")
        response = auth_client.patch(url, {"naam": "Nieuwe Naam", "telefoon": "0612345678"})
        assert response.status_code == 200
        assert response.data["naam"] == "Nieuwe Naam"
        assert response.data["telefoon"] == "0612345678"

    def test_profiel_email_niet_wijzigbaar(self, auth_client):
        url = reverse("api:profiel-mij")
        response = auth_client.patch(url, {"email": "ander@email.nl"})
        assert response.status_code == 200
        assert response.data["email"] == "gebruik@utrecht.nl"  # Ongewijzigd

    def test_profiel_zonder_auth(self, api_client):
        url = reverse("api:profiel-mij")
        response = api_client.get(url)
        assert response.status_code == 401
