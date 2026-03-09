from django.conf import settings
from django.contrib.auth import authenticate
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.api.permissions import IsFullyAuthenticated, IsTOTPPending
from apps.gebruikers.models import User
from apps.gebruikers.serializers import UserProfileSerializer, UserRegistratieSerializer

# ── Cookie-helpers ────────────────────────────────────────────────────────────

def _cookie_auth_actief() -> bool:
    """Geeft True terug als cookie-gebaseerde JWT-auth is ingeschakeld."""
    return getattr(settings, "JWT_AUTH_COOKIE_ENABLED", False)


def _stel_auth_cookies_in(response, access_token: str, refresh_token: str) -> None:
    """Stel HttpOnly JWT-cookies in op de response (alleen in cookie-modus)."""
    if not _cookie_auth_actief():
        return

    access_lifetime = settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME")
    refresh_lifetime = settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME")
    secure = getattr(settings, "JWT_AUTH_COOKIE_SECURE", False)
    samesite = getattr(settings, "JWT_AUTH_COOKIE_SAMESITE", "Strict")

    response.set_cookie(
        key=getattr(settings, "JWT_AUTH_COOKIE", "swc_access"),
        value=access_token,
        max_age=int(access_lifetime.total_seconds()) if access_lifetime else 1800,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/",
    )
    response.set_cookie(
        key=getattr(settings, "JWT_AUTH_REFRESH_COOKIE", "swc_refresh"),
        value=refresh_token,
        max_age=int(refresh_lifetime.total_seconds()) if refresh_lifetime else 86400,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/",
    )


def _wis_auth_cookies(response) -> None:
    """Verwijder de JWT-cookies van de response (alleen in cookie-modus)."""
    if not _cookie_auth_actief():
        return

    samesite = getattr(settings, "JWT_AUTH_COOKIE_SAMESITE", "Strict")
    response.delete_cookie(
        key=getattr(settings, "JWT_AUTH_COOKIE", "swc_access"),
        path="/",
        samesite=samesite,
    )
    response.delete_cookie(
        key=getattr(settings, "JWT_AUTH_REFRESH_COOKIE", "swc_refresh"),
        path="/",
        samesite=samesite,
    )


# ── Views ─────────────────────────────────────────────────────────────────────

class LoginView(APIView):
    """
    Stap 1 van login: e-mail + wachtwoord.
    Retourneert een tijdelijk token als 2FA is ingeschakeld,
    of direct JWT tokens als 2FA niet is ingeschakeld.
    In cookie-modus worden de tokens tevens als HttpOnly-cookie ingesteld.
    """
    permission_classes = [AllowAny]

    def dispatch(self, request, *args, **kwargs):
        # CSRF exempt voor deze view
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"detail": "E-mailadres en wachtwoord zijn verplicht."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response(
                {"detail": "Ongeldige inloggegevens."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.status == "wacht_op_fiattering":
            return Response(
                {"detail": "Uw account wacht nog op goedkeuring."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if user.status == "inactief":
            return Response(
                {"detail": "Uw account is gedeactiveerd."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check of 2FA is ingeschakeld
        if user.totp_enabled:
            # Genereer tijdelijk token voor 2FA verificatie
            temp_token = RefreshToken.for_user(user)
            temp_token["totp_pending"] = True
            return Response({
                "totp_required": True,
                "temp_token": str(temp_token.access_token),
            })

        # Geen 2FA: direct inloggen
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        response = Response({
            "totp_required": False,
            "access": access,
            "refresh": str(refresh),
            "user": UserProfileSerializer(user).data,
        })
        _stel_auth_cookies_in(response, access, str(refresh))
        return response


class VerifyTOTPView(APIView):
    """
    Stap 2 van login: TOTP code verificatie.

    Accepteert uitsluitend een pre-2FA token (totp_pending=True).
    Na succesvolle verificatie worden normale access/refresh tokens uitgegeven.
    In cookie-modus worden de tokens tevens als HttpOnly-cookie ingesteld.
    """
    permission_classes = [IsTOTPPending]

    def post(self, request):
        totp_code = request.data.get("totp_code")
        if not totp_code:
            return Response(
                {"detail": "TOTP code is verplicht."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        devices = TOTPDevice.objects.filter(user=user, confirmed=True)

        verified = False
        for device in devices:
            if device.verify_token(totp_code):
                verified = True
                break

        if not verified:
            return Response(
                {"detail": "Ongeldige TOTP code."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        response = Response({
            "access": access,
            "refresh": str(refresh),
            "user": UserProfileSerializer(user).data,
        })
        _stel_auth_cookies_in(response, access, str(refresh))
        return response


class RegistratieView(APIView):
    """Gebruikersregistratie."""
    permission_classes = [AllowAny]

    def dispatch(self, request, *args, **kwargs):
        # CSRF exempt voor deze view
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        serializer = UserRegistratieSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "detail": "Registratie succesvol. Uw account wacht op goedkeuring.",
                "user_id": str(user.id),
            },
            status=status.HTTP_201_CREATED,
        )


class LogoutView(APIView):
    """
    Logout: blacklist het refresh token.
    In cookie-modus wordt het refresh token uit de cookie gelezen en worden
    beide cookies gewist.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Lees refresh token uit request body; val terug op cookie in cookie-modus
        refresh_token = request.data.get("refresh")
        if not refresh_token and _cookie_auth_actief():
            refresh_token = request.COOKIES.get(
                getattr(settings, "JWT_AUTH_REFRESH_COOKIE", "swc_refresh")
            )

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass

        response = Response({"detail": "Uitgelogd."})
        _wis_auth_cookies(response)
        return response


class WachtwoordResetRequestView(APIView):
    """Wachtwoord reset aanvragen (stuurt e-mail)."""
    permission_classes = [AllowAny]

    def dispatch(self, request, *args, **kwargs):
        # CSRF exempt voor deze view
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        email = request.data.get("email")
        # Altijd succesbericht retourneren (voorkom email enumeration)
        if email:
            try:
                _user = User.objects.get(email=email)  # noqa: F841
                # TODO: Stuur wachtwoord-reset e-mail via Celery
                # send_password_reset_email.delay(_user.id)
            except User.DoesNotExist:
                pass
        return Response(
            {"detail": "Als het e-mailadres bij ons bekend is, ontvangt u een reset-link."}
        )


class TOTPSetupView(APIView):
    """2FA TOTP setup: genereer een nieuw TOTP device met QR code."""
    permission_classes = [IsFullyAuthenticated]

    def post(self, request):
        user = request.user
        # Verwijder onbevestigde devices
        TOTPDevice.objects.filter(user=user, confirmed=False).delete()

        device = TOTPDevice.objects.create(
            user=user,
            name=f"Softwarecatalogus ({user.email})",
            confirmed=False,
        )

        config_url = device.config_url
        return Response({
            "config_url": config_url,
            "detail": "Scan de QR code met uw authenticator app en bevestig met een code.",
        })

    def put(self, request):
        """Bevestig TOTP setup met een code."""
        totp_code = request.data.get("totp_code")
        if not totp_code:
            return Response(
                {"detail": "TOTP code is verplicht."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        device = TOTPDevice.objects.filter(user=user, confirmed=False).first()
        if not device:
            return Response(
                {"detail": "Geen TOTP setup gevonden. Start opnieuw."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if device.verify_token(totp_code):
            device.confirmed = True
            device.save()
            user.totp_enabled = True
            user.save(update_fields=["totp_enabled"])
            return Response({"detail": "2FA is succesvol ingeschakeld."})

        return Response(
            {"detail": "Ongeldige code. Probeer opnieuw."},
            status=status.HTTP_400_BAD_REQUEST,
        )
