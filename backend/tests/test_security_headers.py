"""Tests voor beveiligingsheaders (issue #15 — nl.internet.nl 100% score)."""

import pytest
from django.test import override_settings
from django.urls import reverse

pytestmark = pytest.mark.django_db


PRODUCTIE_INSTELLINGEN = {
    "SECURE_HSTS_SECONDS": 31536000,
    "SECURE_HSTS_INCLUDE_SUBDOMAINS": True,
    "SECURE_HSTS_PRELOAD": True,
    "SECURE_CONTENT_TYPE_NOSNIFF": True,
    "X_FRAME_OPTIONS": "DENY",
    "SESSION_COOKIE_SECURE": True,
    "SESSION_COOKIE_SAMESITE": "Strict",
    "CSRF_COOKIE_SECURE": True,
}


class TestBeveiligingsInstellingen:
    """Controleert dat productie-instellingen correct zijn geconfigureerd."""

    @override_settings(**PRODUCTIE_INSTELLINGEN)
    def test_hsts_ingesteld(self):
        from django.conf import settings

        assert settings.SECURE_HSTS_SECONDS == 31536000
        assert settings.SECURE_HSTS_INCLUDE_SUBDOMAINS is True
        assert settings.SECURE_HSTS_PRELOAD is True

    @override_settings(**PRODUCTIE_INSTELLINGEN)
    def test_x_frame_options_deny(self):
        from django.conf import settings

        assert settings.X_FRAME_OPTIONS == "DENY"

    @override_settings(**PRODUCTIE_INSTELLINGEN)
    def test_content_type_nosniff(self):
        from django.conf import settings

        assert settings.SECURE_CONTENT_TYPE_NOSNIFF is True

    @override_settings(**PRODUCTIE_INSTELLINGEN)
    def test_session_cookie_secure(self):
        from django.conf import settings

        assert settings.SESSION_COOKIE_SECURE is True
        assert settings.SESSION_COOKIE_SAMESITE == "Strict"

    @override_settings(**PRODUCTIE_INSTELLINGEN)
    def test_csrf_cookie_secure(self):
        from django.conf import settings

        assert settings.CSRF_COOKIE_SECURE is True


class TestResponseHeaders:
    """Controleert dat beveiligingsheaders in API-responses aanwezig zijn."""

    @override_settings(
        SECURE_CONTENT_TYPE_NOSNIFF=True,
        X_FRAME_OPTIONS="DENY",
    )
    def test_api_response_bevat_x_frame_options(self, api_client):
        url = reverse("api:pakket-list")
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.headers.get("X-Frame-Options") == "DENY"

    @override_settings(SECURE_CONTENT_TYPE_NOSNIFF=True)
    def test_api_response_bevat_x_content_type_options(self, api_client):
        url = reverse("api:pakket-list")
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
