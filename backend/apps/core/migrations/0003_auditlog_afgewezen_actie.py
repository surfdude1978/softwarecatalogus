"""Migratie: AFGEWEZEN actie toevoegen aan AuditLog."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_rename_core_audit_actor_idx_core_auditl_actor_i_118155_idx_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="auditlog",
            name="actie",
            field=models.CharField(
                choices=[
                    ("aangemaakt", "Aangemaakt"),
                    ("bijgewerkt", "Bijgewerkt"),
                    ("verwijderd", "Verwijderd"),
                    ("ingelogd", "Ingelogd"),
                    ("uitgelogd", "Uitgelogd"),
                    ("export", "Export"),
                    ("import", "Import"),
                    ("gefiateerd", "Gefiateerd"),
                    ("afgewezen", "Afgewezen"),
                ],
                max_length=20,
            ),
        ),
    ]
