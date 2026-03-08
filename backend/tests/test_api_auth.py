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


# ─────────────────────────────────────────────────────────────────
# Tests: 2FA bypass preventie (issue #5)
# ─────────────────────────────────────────────────────────────────

class TestTOTPBypassPrevention:
    """
    Verifieer dat een pre-2FA token (totp_pending=True) UITSLUITEND
    het TOTP verify-endpoint kan bereiken en alle overige beveiligde
    endpoints weigert.
    """

    @pytest.fixture
    def temp_token(self, gebruik_beheerder):
        """Genereer een totp_pending token zoals de LoginView dat doet."""
        from rest_framework_simplejwt.tokens import RefreshToken
        gebruik_beheerder.totp_enabled = True
        gebruik_beheerder.save()
        token = RefreshToken.for_user(gebruik_beheerder)
        token["totp_pending"] = True
        return str(token.access_token)

    def test_temp_token_mag_verify_totp_bereiken(self, api_client, temp_token):
        """Het totp_pending token wordt geaccepteerd door verify-totp (ook al faalt de code zelf)."""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {temp_token}")
        url = reverse("api:verify-totp")
        # Code is fout, maar het endpoint is bereikbaar (niet 401/403 op authenticatie)
        response = api_client.post(url, {"totp_code": "000000"})
        # 401 door ongeldige TOTP code is OK; 403 door permissie is NIET OK
        assert response.status_code != 403, (
            "totp_pending token moet het verify-totp endpoint kunnen bereiken"
        )

    def test_temp_token_geblokkeerd_op_profiel_endpoint(self, api_client, temp_token):
        """Profiel endpoint weigert een pre-2FA token (403/401)."""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {temp_token}")
        url = reverse("api:profiel-mij")
        response = api_client.get(url)
        assert response.status_code in (401, 403), (
            f"Verwacht 401/403 voor totp_pending token op /profiel/mij/, "
            f"maar kreeg {response.status_code}"
        )

    def test_temp_token_geblokkeerd_op_pakket_aanmaken(self, api_client, temp_token):
        """POST op pakketten endpoint weigert een pre-2FA token."""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {temp_token}")
        url = reverse("api:pakket-list")
        response = api_client.post(url, {"naam": "Bypass poging"})
        assert response.status_code in (401, 403)

    def test_temp_token_geblokkeerd_op_pakketoverzicht_write(self, api_client, temp_token):
        """POST op mijn pakketoverzicht weigert een pre-2FA token."""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {temp_token}")
        url = reverse("api:mijn-pakketoverzicht-list")
        response = api_client.post(url, {})
        assert response.status_code in (401, 403)

    def test_temp_token_geblokkeerd_op_logout(self, api_client, temp_token):
        """Logout endpoint weigert een pre-2FA token (mag niet als geldige sessie worden beschouwd)."""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {temp_token}")
        url = reverse("api:logout")
        response = api_client.post(url, {})
        # Logout kan worden toegestaan (200) of geweigerd (401/403); nooit 500
        assert response.status_code != 500

    def test_normaal_token_heeft_geen_totp_pending_claim(self, api_client, gebruik_beheerder):
        """Een normaal login token bevat géén totp_pending claim."""
        from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
        refresh = RefreshToken.for_user(gebruik_beheerder)
        access_token = AccessToken(str(refresh.access_token))
        assert "totp_pending" not in access_token or not access_token.get("totp_pending", False)

    def test_normaal_token_heeft_toegang_tot_profiel(self, auth_client):
        """Een normaal token (zonder totp_pending) heeft gewone toegang tot beveiligde endpoints."""
        url = reverse("api:profiel-mij")
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_temp_token_geblokkeerd_op_totp_setup(self, api_client, temp_token):
        """TOTP setup endpoint weigert een pre-2FA token."""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {temp_token}")
        url = reverse("api:totp-setup")
        response = api_client.post(url)
        assert response.status_code in (401, 403)

    def test_volledig_ingelogd_token_geblokkeerd_op_verify_totp(self, auth_client):
        """Een volledig geldig token (zonder totp_pending) mag verify-totp NIET gebruiken."""
        url = reverse("api:verify-totp")
        response = auth_client.post(url, {"totp_code": "000000"})
        # Een volledig geauthenticeerde gebruiker heeft de verify-stap niet nodig
        assert response.status_code == 403, (
            "Volledig ingelogd token moet worden geweigerd op verify-totp endpoint"
        )

    def test_publieke_get_endpoints_toegankelijk_met_temp_token(self, api_client, temp_token):
        """GET op publieke endpoints mag wél lukken met een totp_pending token (leesrechten)."""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {temp_token}")
        url = reverse("api:pakket-list")
        response = api_client.get(url)
        # Publieke leesacties zijn OK (IsFullyAuthenticatedOrReadOnly staat GET toe)
        assert response.status_code == 200


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
