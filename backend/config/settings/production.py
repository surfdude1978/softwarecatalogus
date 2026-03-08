"""Production settings."""
from .base import *  # noqa: F401, F403

DEBUG = False

# ── HTTPS en HSTS (nl.internet.nl vereisten) ──────────────────────────────
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000          # 1 jaar
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ── Cookie beveiliging ─────────────────────────────────────────────────────
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Strict"

# ── Browser beveiligingsheaders ────────────────────────────────────────────
SECURE_CONTENT_TYPE_NOSNIFF = True       # X-Content-Type-Options: nosniff
X_FRAME_OPTIONS = "DENY"                 # X-Frame-Options: DENY

# ── Cookie-gebaseerde JWT auth (veilig in productie) ──────────────────────
JWT_AUTH_COOKIE_ENABLED = True
JWT_AUTH_COOKIE_SECURE = True

# ── CORS — alleen productiedomein toestaan ─────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    "https://softwarecatalogus.nl",
    "https://www.softwarecatalogus.nl",
]
