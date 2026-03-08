"""Aangepaste JWT authenticatie die bij een ongeldig token anoniem doorgaat."""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class OptionalJWTAuthentication(JWTAuthentication):
    """
    JWT authenticatie waarbij een ongeldig of verlopen token niet resulteert
    in een 401-fout, maar de gebruiker als anoniem wordt behandeld.

    Dit maakt het mogelijk dat publieke endpoints bereikbaar zijn zonder token,
    terwijl een geldig token wél de gebruiker identificeert.
    """

    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except (InvalidToken, TokenError):
            return None
