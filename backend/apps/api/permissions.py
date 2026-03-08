"""Custom permissies voor de Softwarecatalogus API."""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAanbodBeheerder(BasePermission):
    """Alleen aanbod-beheerders (leveranciers) mogen pakketten beheren."""
    def has_permission(self, request, view):
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
