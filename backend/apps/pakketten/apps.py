from django.apps import AppConfig


class PakkettenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pakketten"
    verbose_name = "Pakketten"

    def ready(self):
        import apps.pakketten.signals  # noqa: F401
