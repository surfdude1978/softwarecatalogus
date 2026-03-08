"""Production settings."""
from .base import *  # noqa: F401, F403

DEBUG = False

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Cookie-gebaseerde JWT auth (veilig in productie)
JWT_AUTH_COOKIE_ENABLED = True
JWT_AUTH_COOKIE_SECURE = True

# CORS - aanpassen aan productiedomein
CORS_ALLOWED_ORIGINS = [
    "https://softwarecatalogus.nl",
    "https://www.softwarecatalogus.nl",
]
