"""Tests voor custom permission classes."""

from unittest.mock import MagicMock

import pytest

from apps.api.permissions import (
    IsAanbodBeheerder,
    IsEigenOrganisatie,
    IsFullyAuthenticated,
    IsFullyAuthenticatedOrReadOnly,
    IsFunctioneelBeheerder,
    IsGebruikBeheerder,
    IsTOTPPending,
)

pytestmark = pytest.mark.django_db


def _make_request(user, method="GET", totp_pending=False):
    """
    Maak een MagicMock request aan.

    ``_totp_pending`` wordt expliciet ingesteld zodat MagicMock het attribuut
    niet automatisch als een truthy MagicMock-object aanmaakt.
    """
    request = MagicMock()
    request.user = user
    request.method = method
    request._totp_pending = totp_pending  # Expliciet False om MagicMock-auto-attribuut te voorkomen
    return request


# ========================
# IsAanbodBeheerder
# ========================


class TestIsAanbodBeheerder:
    def test_safe_methods_altijd_toegestaan(self, gebruiker_publiek):
        perm = IsAanbodBeheerder()
        for method in ["GET", "HEAD", "OPTIONS"]:
            request = _make_request(gebruiker_publiek, method)
            assert perm.has_permission(request, None) is True

    def test_write_als_aanbod_beheerder(self, aanbod_beheerder):
        perm = IsAanbodBeheerder()
        request = _make_request(aanbod_beheerder, "POST")
        assert perm.has_permission(request, None) is True

    def test_write_als_functioneel_beheerder(self, functioneel_beheerder):
        perm = IsAanbodBeheerder()
        request = _make_request(functioneel_beheerder, "POST")
        assert perm.has_permission(request, None) is True

    def test_write_als_gebruik_beheerder_verboden(self, gebruik_beheerder):
        perm = IsAanbodBeheerder()
        request = _make_request(gebruik_beheerder, "POST")
        assert perm.has_permission(request, None) is False

    def test_object_permission_eigen_leverancier(self, aanbod_beheerder, pakket, leverancier):
        perm = IsAanbodBeheerder()
        request = _make_request(aanbod_beheerder, "PUT")
        assert perm.has_object_permission(request, None, pakket) is True

    def test_object_permission_andere_leverancier(self, aanbod_beheerder, db):
        from apps.organisaties.models import Organisatie
        from apps.pakketten.models import Pakket

        andere_lev = Organisatie.objects.create(naam="Andere", type="leverancier", status="actief")
        ander_pakket = Pakket.objects.create(naam="X", leverancier=andere_lev)
        perm = IsAanbodBeheerder()
        request = _make_request(aanbod_beheerder, "PUT")
        assert perm.has_object_permission(request, None, ander_pakket) is False


# ========================
# IsGebruikBeheerder
# ========================


class TestIsGebruikBeheerder:
    def test_read_als_ingelogd(self, gebruik_beheerder):
        perm = IsGebruikBeheerder()
        request = _make_request(gebruik_beheerder, "GET")
        assert perm.has_permission(request, None) is True

    def test_read_als_anoniem_verboden(self, db):
        perm = IsGebruikBeheerder()
        user = MagicMock()
        user.is_authenticated = False
        request = _make_request(user, "GET")
        assert perm.has_permission(request, None) is False

    def test_write_als_gebruik_beheerder(self, gebruik_beheerder):
        perm = IsGebruikBeheerder()
        request = _make_request(gebruik_beheerder, "POST")
        assert perm.has_permission(request, None) is True

    def test_write_als_publiek_verboden(self, gebruiker_publiek):
        perm = IsGebruikBeheerder()
        request = _make_request(gebruiker_publiek, "POST")
        assert perm.has_permission(request, None) is False

    def test_object_permission_eigen_organisatie(self, gebruik_beheerder, pakket_gebruik):
        perm = IsGebruikBeheerder()
        request = _make_request(gebruik_beheerder, "DELETE")
        assert perm.has_object_permission(request, None, pakket_gebruik) is True


# ========================
# IsFunctioneelBeheerder
# ========================


class TestIsFunctioneelBeheerder:
    def test_functioneel_beheerder_heeft_toegang(self, functioneel_beheerder):
        perm = IsFunctioneelBeheerder()
        request = _make_request(functioneel_beheerder, "POST")
        assert perm.has_permission(request, None) is True

    def test_gebruik_beheerder_geen_admin_toegang(self, gebruik_beheerder):
        perm = IsFunctioneelBeheerder()
        request = _make_request(gebruik_beheerder, "GET")
        assert perm.has_permission(request, None) is False

    def test_anoniem_geen_admin_toegang(self, db):
        perm = IsFunctioneelBeheerder()
        user = MagicMock()
        user.is_authenticated = False
        request = _make_request(user, "GET")
        assert perm.has_permission(request, None) is False


# ========================
# IsEigenOrganisatie
# ========================


class TestIsEigenOrganisatie:
    def test_safe_methods_altijd_toegestaan(self, gebruik_beheerder, pakket):
        perm = IsEigenOrganisatie()
        request = _make_request(gebruik_beheerder, "GET")
        assert perm.has_object_permission(request, None, pakket) is True

    def test_eigen_organisatie_object(self, gebruik_beheerder, pakket_gebruik):
        perm = IsEigenOrganisatie()
        request = _make_request(gebruik_beheerder, "PUT")
        assert perm.has_object_permission(request, None, pakket_gebruik) is True

    def test_andere_organisatie_verboden(self, gebruik_beheerder, pakket, gemeente2):
        from apps.pakketten.models import PakketGebruik

        ander_gebruik = PakketGebruik.objects.create(pakket=pakket, organisatie=gemeente2, status="in_gebruik")
        perm = IsEigenOrganisatie()
        request = _make_request(gebruik_beheerder, "PUT")
        assert perm.has_object_permission(request, None, ander_gebruik) is False

    def test_functioneel_beheerder_altijd_toegang(self, functioneel_beheerder, pakket_gebruik):
        perm = IsEigenOrganisatie()
        request = _make_request(functioneel_beheerder, "DELETE")
        assert perm.has_object_permission(request, None, pakket_gebruik) is True


# ───────────────────────────────────────────────────────────────────────────
# Tests: 2FA-bewuste permissieklassen (issue #5)
# ───────────────────────────────────────────────────────────────────────────


class TestIsFullyAuthenticated:
    def test_volledig_ingelogd_heeft_toegang(self, gebruik_beheerder):
        perm = IsFullyAuthenticated()
        request = _make_request(gebruik_beheerder, "GET")
        assert perm.has_permission(request, None) is True

    def test_totp_pending_token_geweigerd(self, gebruik_beheerder):
        perm = IsFullyAuthenticated()
        request = _make_request(gebruik_beheerder, "GET", totp_pending=True)
        assert perm.has_permission(request, None) is False

    def test_anoniem_geweigerd(self, db):
        perm = IsFullyAuthenticated()
        user = MagicMock()
        user.is_authenticated = False
        request = _make_request(user, "GET")
        assert perm.has_permission(request, None) is False


class TestIsFullyAuthenticatedOrReadOnly:
    def test_get_anoniem_toegestaan(self, db):
        perm = IsFullyAuthenticatedOrReadOnly()
        user = MagicMock()
        user.is_authenticated = False
        request = _make_request(user, "GET")
        assert perm.has_permission(request, None) is True

    def test_get_met_totp_pending_toegestaan(self, gebruik_beheerder):
        """Leesacties met totp_pending token zijn toegestaan (anoniem-equivalent)."""
        perm = IsFullyAuthenticatedOrReadOnly()
        request = _make_request(gebruik_beheerder, "GET", totp_pending=True)
        assert perm.has_permission(request, None) is True

    def test_post_met_totp_pending_geweigerd(self, gebruik_beheerder):
        perm = IsFullyAuthenticatedOrReadOnly()
        request = _make_request(gebruik_beheerder, "POST", totp_pending=True)
        assert perm.has_permission(request, None) is False

    def test_post_volledig_ingelogd_toegestaan(self, gebruik_beheerder):
        perm = IsFullyAuthenticatedOrReadOnly()
        request = _make_request(gebruik_beheerder, "POST")
        assert perm.has_permission(request, None) is True

    def test_post_anoniem_geweigerd(self, db):
        perm = IsFullyAuthenticatedOrReadOnly()
        user = MagicMock()
        user.is_authenticated = False
        request = _make_request(user, "POST")
        assert perm.has_permission(request, None) is False


class TestIsTOTPPending:
    def test_totp_pending_token_heeft_toegang(self, gebruik_beheerder):
        perm = IsTOTPPending()
        request = _make_request(gebruik_beheerder, "POST", totp_pending=True)
        assert perm.has_permission(request, None) is True

    def test_volledig_ingelogd_geweigerd(self, gebruik_beheerder):
        """Volledig ingelogde gebruiker mag verify-totp niet gebruiken."""
        perm = IsTOTPPending()
        request = _make_request(gebruik_beheerder, "POST", totp_pending=False)
        assert perm.has_permission(request, None) is False

    def test_anoniem_geweigerd(self, db):
        perm = IsTOTPPending()
        user = MagicMock()
        user.is_authenticated = False
        request = _make_request(user, "POST")
        assert perm.has_permission(request, None) is False


class TestTOTPPendingBlockingInCustomPermissions:
    """Verifieer dat bestaande custom permissies ook totp_pending blokkeren."""

    def test_aanbod_beheerder_safe_methods_geweigerd_met_totp_pending(self, gebruiker_publiek):
        perm = IsAanbodBeheerder()
        request = _make_request(gebruiker_publiek, "GET", totp_pending=True)
        assert perm.has_permission(request, None) is False

    def test_gebruik_beheerder_geweigerd_met_totp_pending(self, gebruik_beheerder):
        perm = IsGebruikBeheerder()
        request = _make_request(gebruik_beheerder, "GET", totp_pending=True)
        assert perm.has_permission(request, None) is False

    def test_functioneel_beheerder_geweigerd_met_totp_pending(self, functioneel_beheerder):
        perm = IsFunctioneelBeheerder()
        request = _make_request(functioneel_beheerder, "POST", totp_pending=True)
        assert perm.has_permission(request, None) is False
