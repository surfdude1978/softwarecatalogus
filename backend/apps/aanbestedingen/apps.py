"""App configuratie voor TenderNed aanbestedingen integratie."""
from django.apps import AppConfig


class AanbestedingenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.aanbestedingen"
    verbose_name = "Aanbestedingen (TenderNed)"

    def ready(self):
        pass  # Signals registreren indien nodig
