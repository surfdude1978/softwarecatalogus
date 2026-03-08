"""Tests voor cookie-gebaseerde JWT authenticatie (issue #6)."""
import pytest
from django.test import override_settings
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

pytestmark = pytest.mark.django_db

# ── Hulpinstellingen ──────────────────────────────────────────────────────────

COOKIE_MODUS = {
    "JWT_AUTH_COOKIE_ENABLED": True,
    "JWT_AUTH_COOKIE": "swc_access",
    "JWT_AUTH_REFRESH_COOKIE": "swc_refresh",
    "JWT_AUTH_COOKIE_SECURE": False,
    "JWT_AUTH_COOKIE_SAMESITE": "Strict",
}


# ── OptionalJWTAuthentication ─────────────────────────────────────────────────

class TestCookieAuthentication:
    """OptionalJWTAuthentication leest cookie of Authorization-header."""

    @override_settings(**COOKIE_MODUS)
    def test_authenticeer_via_access_cookie(self, api_client, gebruik_beheerder):
        """Geldig access-cookie → gebruiker geïdentificeerd."""
        refresh = RefreshToken.for_user(gebruik_beheerder)
        api_client.cookies["swc_access"] = str(refresh.access_token)

        url = reverse("api:profiel-mij")
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["email"] == gebruik_beheerder.email

    @override_settings(**COOKIE_MODUS)
    def test_cookie_heeft_voorrang_boven_header(
        self, api_client, gebruik_beheerder, functioneel_beheerder
    ):
        """Als zowel cookie als header aanwezig zijn, wint het cookie."""
        refresh_cookie = RefreshToken.for_user(gebruik_beheerder)
        refresh_header = RefreshToken.for_user(functioneel_beheerder)

        api_client.cookies["swc_access"] = str(refresh_cookie.access_token)
        api_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh_header.access_token}"
        )

        url = reverse("api:profiel-mij")
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["email"] == gebruik_beheerder.email

    @override_settings(**COOKIE_MODUS)
    def test_valback_naar_header_zonder_cookie(self, api_client, gebruik_beheerder):
        """Zonder cookie werkt de Authorization-header nog steeds."""
        refresh = RefreshToken.for_user(gebruik_beheerder)
        api_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

        url = reverse("api:profiel-mij")
        response = api_client.get(url)

        assert response.status_code == 200

    @override_settings(**COOKIE_MODUS)
    def test_ongeldige_cookie_geeft_anonieme_toegang(self, api_client):
        """Een ongeldige cookie levert geen 401 maar anonieme toegang op (optioneel)."""
        api_client.cookies["swc_access"] = "ongeldig.jwt.token"

        url = reverse("api:pakket-list")
        response = api_client.get(url)

        # Publiek endpoint moet nog steeds bereikbaar zijn
        assert response.status_code == 200

    def test_cookie_auth_uitgeschakeld_negeert_cookie(
        self, api_client, gebruik_beheerder
    ):
        """Met JWT_AUTH_COOKIE_ENABLED=False wordt het cookie genegeerd."""
        refresh = RefreshToken.for_user(gebruik_beheerder)
        api_client.cookies["swc_access"] = str(refresh.access_token)
        # Geen Authorization-header ingesteld

        url = reverse("api:profiel-mij")
        response = api_client.get(url)

        # Geen header én cookie auth uitgeschakeld → anoniem → 401
        assert response.status_code == 401

    @override_settings(**COOKIE_MODUS)
    def test_geen_token_geeft_anonieme_toegang(self, api_client):
        """Geen cookie én geen header → anonieme toegang op publieke endpoints."""
        url = reverse("api:pakket-list")
        response = api_client.get(url)

        assert response.status_code == 200


# ── LoginView ─────────────────────────────────────────────────────────────────

class TestLoginCookies:
    """LoginView stelt HttpOnly-cookies in wanneer cookie-modus actief is."""

    @override_settings(**COOKIE_MODUS)
    def test_login_stelt_access_en_refresh_cookie_in(
        self, api_client, gebruik_beheerder
    ):
        """Na geslaagde login zonder 2FA zijn swc_access en swc_refresh aanwezig."""
        url = reverse("api:login")
        response = api_client.post(
            url,
            {"email": "gebruik@utrecht.nl", "password": "TestWachtwoord123!"},
            format="json",
        )

        assert response.status_code == 200
        assert "swc_access" in response.cookies
        assert "swc_refresh" in response.cookies

    @override_settings(**COOKIE_MODUS)
    def test_login_cookie_is_httponly(self, api_client, gebruik_beheerder):
        """Access-cookie moet httponly zijn (XSS-bescherming)."""
        url = reverse("api:login")
        response = api_client.post(
            url,
            {"email": "gebruik@utrecht.nl", "password": "TestWachtwoord123!"},
            format="json",
        )

        assert response.cookies["swc_access"]["httponly"]
        assert response.cookies["swc_refresh"]["httponly"]

    @override_settings(**COOKIE_MODUS)
    def test_login_cookie_samesite_strict(self, api_client, gebruik_beheerder):
        """Cookie moet SameSite=Strict hebben voor CSRF-bescherming."""
        url = reverse("api:login")
        response = api_client.post(
            url,
            {"email": "gebruik@utrecht.nl", "password": "TestWachtwoord123!"},
            format="json",
        )

        assert response.cookies["swc_access"]["samesite"] == "Strict"

    @override_settings(**COOKIE_MODUS)
    def test_login_retourneert_ook_tokens_in_body(
        self, api_client, gebruik_beheerder
    ):
        """Tokens staan ook in de response body (backwards-compatibiliteit)."""
        url = reverse("api:login")
        response = api_client.post(
            url,
            {"email": "gebruik@utrecht.nl", "password": "TestWachtwoord123!"},
            format="json",
        )

        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_stelt_geen_cookies_in_zonder_instelling(
        self, api_client, gebruik_beheerder
    ):
        """Met JWT_AUTH_COOKIE_ENABLED=False worden er geen JWT-cookies ingesteld."""
        url = reverse("api:login")
        response = api_client.post(
            url,
            {"email": "gebruik@utrecht.nl", "password": "TestWachtwoord123!"},
            format="json",
        )

        assert response.status_code == 200
        assert "swc_access" not in response.cookies
        assert "swc_refresh" not in response.cookies

    @override_settings(**COOKIE_MODUS)
    def test_login_2fa_stelt_geen_cookies_in(
        self, api_client, gebruik_beheerder
    ):
        """Bij 2FA-redirect (temp_token stap) worden nog geen definitieve cookies ingesteld."""
        from django_otp.plugins.otp_totp.models import TOTPDevice
        gebruik_beheerder.totp_enabled = True
        gebruik_beheerder.save()
        TOTPDevice.objects.create(
            user=gebruik_beheerder,
            name="test",
            confirmed=True,
        )

        url = reverse("api:login")
        response = api_client.post(
            url,
            {"email": "gebruik@utrecht.nl", "password": "TestWachtwoord123!"},
            format="json",
        )

        assert response.status_code == 200
        assert response.data["totp_required"] is True
        assert "swc_access" not in response.cookies


# ── LogoutView ────────────────────────────────────────────────────────────────

class TestLogoutCookies:
    """LogoutView wist cookies en accepteert refresh token uit cookie."""

    @override_settings(**COOKIE_MODUS)
    def test_logout_wist_auth_cookies(self, auth_client):
        """Na logout zijn de auth-cookies gewist."""
        url = reverse("api:logout")
        response = auth_client.post(url, {}, format="json")

        assert response.status_code == 200
        # Django's delete_cookie zet de cookie met een lege waarde / max-age=0
        assert "swc_access" in response.cookies
        assert "swc_refresh" in response.cookies

    @override_settings(**COOKIE_MODUS)
    def test_logout_leest_refresh_uit_cookie(self, api_client, gebruik_beheerder):
        """In cookie-modus mag het refresh-token uit de cookie komen (geen body vereist)."""
        refresh = RefreshToken.for_user(gebruik_beheerder)
        api_client.cookies["swc_access"] = str(refresh.access_token)
        api_client.cookies["swc_refresh"] = str(refresh)

        url = reverse("api:logout")
        # Geen refresh in de body
        response = api_client.post(url, {}, format="json")

        assert response.status_code == 200
        assert response.data["detail"] == "Uitgelogd."

    def test_logout_zonder_cookie_modus_werkt_met_body(self, auth_client, gebruik_beheerder):
        """In localStorage-modus werkt logout met refresh in de body."""
        refresh = RefreshToken.for_user(gebruik_beheerder)
        url = reverse("api:logout")
        response = auth_client.post(
            url, {"refresh": str(refresh)}, format="json"
        )

        assert response.status_code == 200

    @override_settings(**COOKIE_MODUS)
    def test_logout_wist_cookies_ook_zonder_refresh(self, auth_client):
        """Cookies worden gewist ook als er geen refresh token beschikbaar is."""
        url = reverse("api:logout")
        response = auth_client.post(url, {}, format="json")

        assert response.status_code == 200
        assert "swc_access" in response.cookies
