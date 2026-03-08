"""Aangepaste JWT authenticatie die bij een ongeldig token anoniem doorgaat."""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class OptionalJWTAuthentication(JWTAuthentication):
    """
    JWT authenticatie waarbij een ongeldig of verlopen token niet resulteert
    in een 401-fout, maar de gebruiker als anoniem wordt behandeld.

    Dit maakt het mogelijk dat publieke endpoints bereikbaar zijn zonder token,
    terwijl een geldig token wél de gebruiker identificeert.

    Bij een geldig token met de claim ``totp_pending=True`` (uitgegeven vóór
    TOTP-verificatie) wordt ``request._totp_pending = True`` gezet.  De
    permissieklassen ``IsFullyAuthenticated`` en
    ``IsFullyAuthenticatedOrReadOnly`` weigeren vervolgens schrijfacties van
    zulke tokens.
    """

    def authenticate(self, request):
        try:
            result = super().authenticate(request)
        except (InvalidToken, TokenError):
            return None

        if result is None:
            return None

        user, validated_token = result
        # Markeer de request als "pre-2FA" zodat permissies dit kunnen blokkeren.
        if validated_token.get("totp_pending", False):
            request._totp_pending = True
        return user, validated_token
