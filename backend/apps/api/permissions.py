"""Custom permissies voor de Softwarecatalogus API."""
from rest_framework.permissions import (
    SAFE_METHODS,
    BasePermission,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)

# ──────────────────────────────────────────────────────────────────────────────
# 2FA-bewuste permissies (issue #5: blokkeer 2FA bypass via totp_pending token)
# ──────────────────────────────────────────────────────────────────────────────

class IsFullyAuthenticated(IsAuthenticated):
    """
    Vereist volledige authenticatie: het JWT-token mag géén ``totp_pending=True``
    claim bevatten.  Gebruik dit op endpoints die nooit bereikbaar mogen zijn
    vóór voltooiing van de TOTP-verificatiestap.
    """

    message = "Twee-factor verificatie vereist. Voltooi de TOTP-verificatiestap."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        # Weiger pre-2FA tokens
        if getattr(request, "_totp_pending", False):
            return False
        return True


class IsFullyAuthenticatedOrReadOnly(IsAuthenticatedOrReadOnly):
    """
    Leesacties (GET/HEAD/OPTIONS): anoniem toegestaan.
    Schrijfacties: volledig geauthenticeerd vereist — een pre-2FA token met de
    claim ``totp_pending=True`` wordt geweigerd.

    Dit is de standaard permissieklasse voor de API (vervangt het generieke
    ``IsAuthenticatedOrReadOnly``).
    """

    message = "Twee-factor verificatie vereist. Voltooi de TOTP-verificatiestap."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        # Schrijfacties vereisen een volledig geauthenticeerde gebruiker
        if request.method not in SAFE_METHODS:
            if getattr(request, "_totp_pending", False):
                return False
        return True


class IsTOTPPending(IsAuthenticated):
    """
    Uitsluitend voor de TOTP-verificatiestap (``/api/v1/auth/token/verify-totp/``).

    Vereist een geldig JWT-token mét de claim ``totp_pending=True``.  Volledig
    ingelogde gebruikers (zonder die claim) worden geweigerd — zij hoeven niet
    nogmaals te verifiëren.
    """

    message = "Dit endpoint accepteert uitsluitend een pre-2FA token."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        # Token moet de totp_pending claim hebben
        if not getattr(request, "_totp_pending", False):
            return False
        return True


class IsAanbodBeheerder(BasePermission):
    """Alleen aanbod-beheerders (leveranciers) mogen pakketten beheren."""
    def has_permission(self, request, view):
        # Weiger pre-2FA tokens ongeacht de methode
        if getattr(request, "_totp_pending", False):
            return False
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and request.user.rol in ["aanbod_beheerder", "functioneel_beheerder"]
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.rol == "functioneel_beheerder":
            return True
        # Aanbod-beheerder mag alleen eigen leverancier-pakketten bewerken
        return (
            hasattr(obj, "leverancier")
            and request.user.organisatie == obj.leverancier
        )


class IsGebruikBeheerder(BasePermission):
    """Alleen gebruik-beheerders mogen eigen pakketlandschap beheren."""
    def has_permission(self, request, view):
        # Weiger pre-2FA tokens — ook leesacties vereisen volledige authenticatie
        if getattr(request, "_totp_pending", False):
            return False
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return (
            request.user.is_authenticated
            and request.user.rol in ["gebruik_beheerder", "functioneel_beheerder"]
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.rol == "functioneel_beheerder":
            return True
        return (
            hasattr(obj, "organisatie")
            and request.user.organisatie == obj.organisatie
        )


class IsFunctioneelBeheerder(BasePermission):
    """Alleen functioneel beheerders hebben volledige admin toegang."""
    def has_permission(self, request, view):
        if getattr(request, "_totp_pending", False):
            return False
        return (
            request.user.is_authenticated
            and request.user.rol == "functioneel_beheerder"
        )


class IsEigenOrganisatie(BasePermission):
    """Gebruiker mag alleen eigen organisatie-data bewerken."""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.rol == "functioneel_beheerder":
            return True
        if hasattr(obj, "organisatie"):
            return request.user.organisatie == obj.organisatie
        if hasattr(obj, "leverancier"):
            return request.user.organisatie == obj.leverancier
        return False
