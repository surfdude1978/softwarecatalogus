"""Authenticatie URL patterns."""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import auth_views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("token/verify-totp/", auth_views.VerifyTOTPView.as_view(), name="verify-totp"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("registreer/", auth_views.RegistratieView.as_view(), name="registreer"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("wachtwoord-reset/", auth_views.WachtwoordResetRequestView.as_view(), name="wachtwoord-reset"),
    path("totp/setup/", auth_views.TOTPSetupView.as_view(), name="totp-setup"),
]
