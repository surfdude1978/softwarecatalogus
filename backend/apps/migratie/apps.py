from django.apps import AppConfig


class MigratieConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.migratie"
    verbose_name = "Data-migratie"
