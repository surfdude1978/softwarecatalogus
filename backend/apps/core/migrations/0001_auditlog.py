"""Migratie: AuditLog model aanmaken."""
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("actor_id", models.CharField(
                    blank=True,
                    help_text="UUID van de gebruiker die de actie uitvoerde (null = anoniem).",
                    max_length=36,
                    null=True,
                )),
                ("actor_email", models.EmailField(
                    blank=True,
                    help_text="E-mailadres ten tijde van de actie (voor historische referentie).",
                    max_length=254,
                )),
                ("actie", models.CharField(
                    choices=[
                        ("aangemaakt", "Aangemaakt"),
                        ("bijgewerkt", "Bijgewerkt"),
                        ("verwijderd", "Verwijderd"),
                        ("ingelogd",   "Ingelogd"),
                        ("uitgelogd",  "Uitgelogd"),
                        ("export",     "Export"),
                        ("import",     "Import"),
                        ("gefiateerd", "Gefiateerd"),
                    ],
                    max_length=20,
                )),
                ("object_type", models.CharField(
                    help_text="Type object waarop de actie werd uitgevoerd (bijv. 'Pakket').",
                    max_length=100,
                )),
                ("object_id", models.CharField(
                    blank=True,
                    help_text="UUID of PK van het object.",
                    max_length=36,
                    null=True,
                )),
                ("object_omschrijving", models.CharField(
                    blank=True,
                    help_text="Leesbare omschrijving van het object (bijv. naam).",
                    max_length=500,
                )),
                ("wijzigingen", models.JSONField(
                    blank=True,
                    default=dict,
                    help_text="Dict van gewijzigde velden: {'veld': {'oud': ..., 'nieuw': ...}}.",
                )),
                ("extra", models.JSONField(
                    blank=True,
                    default=dict,
                    help_text="Aanvullende context (endpoint, parameters, etc.).",
                )),
                ("ip_adres", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.CharField(blank=True, max_length=500)),
                ("tijdstip", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                "verbose_name": "Auditlog",
                "verbose_name_plural": "Auditlogs",
                "ordering": ["-tijdstip"],
            },
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["actor_id", "-tijdstip"], name="core_audit_actor_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["object_type", "object_id"], name="core_audit_object_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["actie", "-tijdstip"], name="core_audit_actie_idx"),
        ),
    ]
