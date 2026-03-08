"""Migratie: EF25 (vrijwillige ex-post-transparantie) toevoegen aan Status-choices."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("aanbestedingen", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="aanbesteding",
            name="status",
            field=models.CharField(
                choices=[
                    ("aankondiging", "Aankondiging van opdracht"),
                    ("gunning", "Aankondiging van gegunde opdracht"),
                    ("rectificatie", "Rectificatie"),
                    ("vooraankondiging", "Vooraankondiging"),
                    ("ef25", "EF25 - Vrijwillige ex-post-transparantie"),
                    ("onbekend", "Onbekend"),
                ],
                default="aankondiging",
                max_length=20,
                verbose_name="Type aankondiging",
            ),
        ),
    ]
