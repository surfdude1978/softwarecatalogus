from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.gebruikers.models import User
from apps.gebruikers.serializers import UserRegistratieSerializer, UserProfileSerializer


class LoginView(APIView):
    """
    Stap 1 van login: e-mail + wachtwoord.
    Retourneert een tijdelijk token als 2FA is ingeschakeld,
    of direct JWT tokens als 2FA niet is ingeschakeld.
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
        return Response({
            "totp_required": False,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserProfileSerializer(user).data,
        })


class VerifyTOTPView(APIView):
    """
    Stap 2 van login: TOTP code verificatie.
    """
    permission_classes = [IsAuthenticated]

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
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserProfileSerializer(user).data,
        })


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
    """Logout: blacklist het refresh token."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        return Response({"detail": "Uitgelogd."})


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
                user = User.objects.get(email=email)
                # TODO: Stuur wachtwoord-reset e-mail via Celery
                # send_password_reset_email.delay(user.id)
            except User.DoesNotExist:
                pass
        return Response(
            {"detail": "Als het e-mailadres bij ons bekend is, ontvangt u een reset-link."}
        )


class TOTPSetupView(APIView):
    """2FA TOTP setup: genereer een nieuw TOTP device met QR code."""
    permission_classes = [IsAuthenticated]

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
