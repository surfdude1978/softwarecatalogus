"""Base Django settings voor Softwarecatalogus."""
import os
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "guardian",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_celery_beat",
    "django_extensions",
]

LOCAL_APPS = [
    "apps.core",
    "apps.gebruikers",
    "apps.organisaties",
    "apps.pakketten",
    "apps.standaarden",
    "apps.architectuur",
    "apps.documenten",
    "apps.content",
    "apps.aanbestedingen",
    "apps.api",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="softwarecatalogus"),
        "USER": config("POSTGRES_USER", default="swc"),
        "PASSWORD": config("POSTGRES_PASSWORD", default="swc"),
        "HOST": config("POSTGRES_HOST", default="db"),
        "PORT": config("POSTGRES_PORT", default="5432"),
    }
}

# Custom User model
AUTH_USER_MODEL = "gebruikers.User"

# Authentication backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "guardian.backends.ObjectPermissionBackend",
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "nl"
TIME_ZONE = "Europe/Amsterdam"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = config("MEDIA_ROOT", default=str(BASE_DIR / "media"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.api.authentication.OptionalJWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        # Vervangt IsAuthenticatedOrReadOnly: weigert totp_pending tokens bij schrijfacties.
        "apps.api.permissions.IsFullyAuthenticatedOrReadOnly",
    ],
    "DEFAULT_METADATA_CLASS": None,
    "CSRF_EXEMPT_VIEWS": ["api.auth_views.LoginView", "api.auth_views.RegistratieView"],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
}

# drf-spectacular (OpenAPI)
SPECTACULAR_SETTINGS = {
    "TITLE": "Softwarecatalogus API",
    "DESCRIPTION": "API voor de Softwarecatalogus van VNG Realisatie — het centrale platform voor gemeentelijke software-registratie.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/v1/",
    "CONTACT": {
        "name": "VNG Realisatie",
        "url": "https://www.vngrealisatie.nl/",
    },
    "LICENSE": {
        "name": "EUPL-1.2",
        "url": "https://eupl.eu/",
    },
}

# SimpleJWT
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Celery
CELERY_BROKER_URL = config("REDIS_URL", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = config("REDIS_URL", default="redis://redis:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/Amsterdam"

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://redis:6379/0"),
    }
}

# Meilisearch
MEILISEARCH_URL = config("MEILISEARCH_URL", default="http://meilisearch:7700")
MEILISEARCH_API_KEY = config("MEILISEARCH_API_KEY", default="masterkey_dev_only")

# Cookie-gebaseerde JWT authenticatie (standaard uit, aan in productie)
JWT_AUTH_COOKIE_ENABLED = config("JWT_AUTH_COOKIE_ENABLED", default=False, cast=bool)
JWT_AUTH_COOKIE = "swc_access"
JWT_AUTH_REFRESH_COOKIE = "swc_refresh"
JWT_AUTH_COOKIE_SECURE = config("JWT_AUTH_COOKIE_SECURE", default=False, cast=bool)
JWT_AUTH_COOKIE_SAMESITE = "Strict"

# CORS
CORS_ALLOW_CREDENTIALS = True  # Vereist voor cookie-gebaseerde cross-origin verzoeken
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost",
    "http://127.0.0.1",
]

# Security
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

# Email
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="smtp.example.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@softwarecatalogus.nl")

# TenderNed Open Data integratie
# Publieke papi REST-endpoint (geen API-sleutel vereist)
TENDERNED_API_URL = config(
    "TENDERNED_API_URL",
    default="https://www.tenderned.nl/papi/tenderned-rs-tns/v2/publicaties",
)
# In development: gebruik voorbeelddata (demo_mode=True).
# In productie wordt dit overschreven naar False via production.py of .env.
TENDERNED_DEMO_MODE = config("TENDERNED_DEMO_MODE", default=True, cast=bool)
TENDERNED_TIMEOUT = config("TENDERNED_TIMEOUT", default=30, cast=int)

# Celery Beat schedule voor dagelijkse TenderNed sync
CELERY_BEAT_SCHEDULE = {
    "sync-tenderned-dagelijks": {
        "task": "aanbestedingen.sync_tenderned",
        "schedule": 86400,  # Elke 24 uur
        "kwargs": {"dagen_terug": 7, "max_resultaten": 500},
    },
}
