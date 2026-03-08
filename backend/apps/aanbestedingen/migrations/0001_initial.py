"""Initiële migratie voor aanbestedingen app."""
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("architectuur", "0002_initial"),
        ("organisaties", "0001_initial"),
        ("pakketten", "0002_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Aanbesteding",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("aangemaakt_op", models.DateTimeField(auto_now_add=True, verbose_name="Aangemaakt op")),
                ("gewijzigd_op", models.DateTimeField(auto_now=True, verbose_name="Gewijzigd op")),
                (
                    "publicatiecode",
                    models.CharField(
                        db_index=True,
                        max_length=100,
                        unique=True,
                        verbose_name="Publicatiecode",
                    ),
                ),
                ("naam", models.CharField(max_length=1000, verbose_name="Naam aanbesteding")),
                (
                    "aanbestedende_dienst",
                    models.CharField(max_length=500, verbose_name="Aanbestedende dienst"),
                ),
                (
                    "aanbestedende_dienst_stad",
                    models.CharField(blank=True, max_length=255, verbose_name="Stad/gemeente"),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("europees", "Europees"),
                            ("nationaal", "Nationaal"),
                            ("onbekend", "Onbekend"),
                        ],
                        default="onbekend",
                        max_length=20,
                        verbose_name="Type aanbesteding",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("aankondiging", "Aankondiging van opdracht"),
                            ("gunning", "Aankondiging van gegunde opdracht"),
                            ("rectificatie", "Rectificatie"),
                            ("vooraankondiging", "Vooraankondiging"),
                            ("onbekend", "Onbekend"),
                        ],
                        default="aankondiging",
                        max_length=20,
                        verbose_name="Type aankondiging",
                    ),
                ),
                (
                    "procedure",
                    models.CharField(blank=True, max_length=200, verbose_name="Procedure"),
                ),
                ("publicatiedatum", models.DateField(verbose_name="Publicatiedatum")),
                (
                    "sluitingsdatum",
                    models.DateField(blank=True, null=True, verbose_name="Sluitingsdatum"),
                ),
                (
                    "cpv_codes",
                    models.JSONField(default=list, verbose_name="CPV-codes"),
                ),
                (
                    "cpv_omschrijvingen",
                    models.JSONField(default=list, verbose_name="CPV-omschrijvingen"),
                ),
                (
                    "waarde_geschat",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=15,
                        null=True,
                        verbose_name="Geschatte waarde (€)",
                    ),
                ),
                (
                    "url_tenderned",
                    models.URLField(max_length=500, verbose_name="URL op TenderNed"),
                ),
                ("omschrijving", models.TextField(blank=True, verbose_name="Omschrijving")),
                (
                    "laatste_sync",
                    models.DateTimeField(auto_now=True, verbose_name="Laatste synchronisatie"),
                ),
                (
                    "gemma_componenten",
                    models.ManyToManyField(
                        blank=True,
                        related_name="aanbestedingen",
                        to="architectuur.gemmacomponent",
                        verbose_name="GEMMA componenten",
                    ),
                ),
                (
                    "organisatie",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="aanbestedingen",
                        to="organisaties.organisatie",
                        verbose_name="Gekoppelde organisatie",
                    ),
                ),
                (
                    "relevante_pakketten",
                    models.ManyToManyField(
                        blank=True,
                        related_name="aanbestedingen",
                        to="pakketten.pakket",
                        verbose_name="Relevante pakketten",
                    ),
                ),
            ],
            options={
                "verbose_name": "Aanbesteding",
                "verbose_name_plural": "Aanbestedingen",
                "ordering": ["-publicatiedatum"],
                "indexes": [
                    models.Index(fields=["-publicatiedatum"], name="aanbesteding_pub_idx"),
                    models.Index(fields=["aanbestedende_dienst"], name="aanbesteding_dienst_idx"),
                ],
            },
        ),
    ]
