"""Aangepaste JWT authenticatie die cookies én Authorization-header ondersteunt."""

from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class OptionalJWTAuthentication(JWTAuthentication):
    """
    JWT authenticatie waarbij een ongeldig of verlopen token niet resulteert
    in een 401-fout, maar de gebruiker als anoniem wordt behandeld.

    Wanneer ``JWT_AUTH_COOKIE_ENABLED = True`` (productie) wordt de access-token
    eerst gelezen uit de ``swc_access`` HttpOnly-cookie.  Daarna valt de klasse
    terug op de standaard ``Authorization: Bearer <token>``-header.

    Dit maakt het mogelijk dat publieke endpoints bereikbaar zijn zonder token,
    terwijl een geldig token wél de gebruiker identificeert.

    Bij een geldig token met de claim ``totp_pending=True`` (uitgegeven vóór
    TOTP-verificatie) wordt ``request._totp_pending = True`` gezet.  De
    permissieklassen ``IsFullyAuthenticated`` en
    ``IsFullyAuthenticatedOrReadOnly`` weigeren vervolgens schrijfacties van
    zulke tokens.
    """

    def authenticate(self, request):
        raw_token = self._haal_raw_token(request)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except (InvalidToken, TokenError):
            return None

        try:
            user = self.get_user(validated_token)
        except (InvalidToken, TokenError):
            return None

        # Markeer de request als "pre-2FA" zodat permissies dit kunnen blokkeren.
        if validated_token.get("totp_pending", False):
            request._totp_pending = True

        return user, validated_token

    def _haal_raw_token(self, request) -> bytes | None:
        """
        Haal de ruwe JWT-token op.

        Volgorde:
        1. HttpOnly-cookie (``JWT_AUTH_COOKIE_ENABLED = True`` vereist)
        2. ``Authorization: Bearer <token>``-header
        """
        if getattr(settings, "JWT_AUTH_COOKIE_ENABLED", False):
            cookie_naam = getattr(settings, "JWT_AUTH_COOKIE", "swc_access")
            cookie_waarde = request.COOKIES.get(cookie_naam)
            if cookie_waarde:
                return cookie_waarde.encode("utf-8")  # type: ignore[no-any-return]

        header = self.get_header(request)
        if header is None:
            return None
        return self.get_raw_token(header)
