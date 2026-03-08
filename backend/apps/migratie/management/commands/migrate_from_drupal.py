"""Management command voor het migreren van data uit de oude Drupal Softwarecatalogus.

Leest CSV-bestanden met data uit de Drupal database en importeert deze
in het nieuwe datamodel. Bewaard originele GUID's als legacy_id voor
referentiele integriteit.

Gebruik:
    python manage.py migrate_from_drupal /pad/naar/export/ --dry-run
    python manage.py migrate_from_drupal /pad/naar/export/
"""
import csv
import logging
import os
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.organisaties.models import Organisatie
from apps.pakketten.models import Pakket, PakketGebruik, Koppeling
from apps.standaarden.models import Standaard, PakketStandaard

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Migreer data uit de oude Drupal Softwarecatalogus (CSV export)"

    def add_arguments(self, parser):
        parser.add_argument(
            "export_dir",
            type=str,
            help="Pad naar de map met CSV-exportbestanden uit Drupal",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Voer geen database wijzigingen door",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Verwijder bestaande gemigreerde data voor een schone import",
        )

    def handle(self, *args, **options):
        export_dir = options["export_dir"]
        dry_run = options["dry_run"]
        clear = options["clear"]

        if not os.path.isdir(export_dir):
            raise CommandError(f"Map niet gevonden: {export_dir}")

        self.stats = {
            "organisaties": {"created": 0, "skipped": 0, "errors": 0},
            "pakketten": {"created": 0, "skipped": 0, "errors": 0},
            "gebruik": {"created": 0, "skipped": 0, "errors": 0},
            "standaarden": {"created": 0, "skipped": 0, "errors": 0},
            "koppelingen": {"created": 0, "skipped": 0, "errors": 0},
        }
        self.errors = []

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — geen wijzigingen worden opgeslagen\n"))

        if clear and not dry_run:
            self._clear_migrated_data()

        try:
            if dry_run:
                self._run_migration(export_dir, dry_run)
            else:
                with transaction.atomic():
                    self._run_migration(export_dir, dry_run)
        except Exception as e:
            raise CommandError(f"Migratie mislukt: {e}")

        self._print_report()

    def _clear_migrated_data(self):
        """Verwijder eerder gemigreerde data."""
        self.stdout.write("Verwijder eerder gemigreerde data...")
        Koppeling.objects.all().delete()
        PakketGebruik.objects.all().delete()
        PakketStandaard.objects.all().delete()
        Pakket.objects.filter(legacy_id__isnull=False).exclude(legacy_id="").delete()
        Organisatie.objects.filter(legacy_id__isnull=False).exclude(legacy_id="").delete()
        self.stdout.write(self.style.SUCCESS("Gemigreerde data verwijderd.\n"))

    def _run_migration(self, export_dir, dry_run):
        """Voer de migratie uit in de juiste volgorde."""
        # 1. Organisaties
        org_file = os.path.join(export_dir, "organisaties.csv")
        if os.path.exists(org_file):
            self._import_organisaties(org_file, dry_run)
        else:
            self.stdout.write(self.style.WARNING(f"  Overgeslagen: {org_file} niet gevonden"))

        # 2. Pakketten
        pakket_file = os.path.join(export_dir, "pakketten.csv")
        if os.path.exists(pakket_file):
            self._import_pakketten(pakket_file, dry_run)
        else:
            self.stdout.write(self.style.WARNING(f"  Overgeslagen: {pakket_file} niet gevonden"))

        # 3. Standaarden
        standaard_file = os.path.join(export_dir, "standaarden.csv")
        if os.path.exists(standaard_file):
            self._import_standaarden(standaard_file, dry_run)
        else:
            self.stdout.write(self.style.WARNING(f"  Overgeslagen: {standaard_file} niet gevonden"))

        # 4. Pakketgebruik
        gebruik_file = os.path.join(export_dir, "pakketgebruik.csv")
        if os.path.exists(gebruik_file):
            self._import_pakketgebruik(gebruik_file, dry_run)
        else:
            self.stdout.write(self.style.WARNING(f"  Overgeslagen: {gebruik_file} niet gevonden"))

        # 5. Koppelingen
        koppeling_file = os.path.join(export_dir, "koppelingen.csv")
        if os.path.exists(koppeling_file):
            self._import_koppelingen(koppeling_file, dry_run)
        else:
            self.stdout.write(self.style.WARNING(f"  Overgeslagen: {koppeling_file} niet gevonden"))

    def _read_csv(self, filepath):
        """Lees een CSV-bestand en retourneer rijen als dicts."""
        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            return list(reader)

    def _import_organisaties(self, filepath, dry_run):
        """Importeer organisaties uit CSV."""
        self.stdout.write(f"\nImporteer organisaties uit {filepath}...")
        rows = self._read_csv(filepath)

        type_mapping = {
            "gemeente": Organisatie.Type.GEMEENTE,
            "leverancier": Organisatie.Type.LEVERANCIER,
            "samenwerkingsverband": Organisatie.Type.SAMENWERKINGSVERBAND,
        }

        for row in rows:
            legacy_id = row.get("guid", row.get("id", "")).strip()
            if not legacy_id:
                self.stats["organisaties"]["skipped"] += 1
                continue

            if Organisatie.objects.filter(legacy_id=legacy_id).exists():
                self.stats["organisaties"]["skipped"] += 1
                continue

            try:
                org_type = type_mapping.get(
                    row.get("type", "").lower().strip(),
                    Organisatie.Type.OVERIG,
                )

                if not dry_run:
                    Organisatie.objects.create(
                        legacy_id=legacy_id,
                        naam=row.get("naam", "Onbekend").strip(),
                        type=org_type,
                        status=Organisatie.Status.ACTIEF,
                        oin=row.get("oin", "").strip(),
                        website=row.get("website", "").strip()[:200],
                        beschrijving=row.get("beschrijving", "").strip(),
                    )
                self.stats["organisaties"]["created"] += 1
            except Exception as e:
                self.stats["organisaties"]["errors"] += 1
                self.errors.append(f"Organisatie {legacy_id}: {e}")

    def _import_pakketten(self, filepath, dry_run):
        """Importeer pakketten uit CSV."""
        self.stdout.write(f"\nImporteer pakketten uit {filepath}...")
        rows = self._read_csv(filepath)

        licentie_mapping = {
            "commercieel": Pakket.Licentievorm.COMMERCIEEL,
            "open source": Pakket.Licentievorm.OPEN_SOURCE,
            "saas": Pakket.Licentievorm.SAAS,
        }

        for row in rows:
            legacy_id = row.get("guid", row.get("id", "")).strip()
            if not legacy_id:
                self.stats["pakketten"]["skipped"] += 1
                continue

            if Pakket.objects.filter(legacy_id=legacy_id).exists():
                self.stats["pakketten"]["skipped"] += 1
                continue

            try:
                leverancier_id = row.get("leverancier_guid", row.get("leverancier_id", "")).strip()
                leverancier = None
                if leverancier_id:
                    leverancier = Organisatie.objects.filter(legacy_id=leverancier_id).first()

                if not leverancier:
                    # Maak een placeholder leverancier
                    leverancier_naam = row.get("leverancier_naam", "Onbekend").strip()
                    if not dry_run:
                        leverancier, _ = Organisatie.objects.get_or_create(
                            naam=leverancier_naam,
                            type=Organisatie.Type.LEVERANCIER,
                            defaults={
                                "status": Organisatie.Status.CONCEPT,
                                "legacy_id": f"auto-{leverancier_naam[:80]}",
                            },
                        )

                licentie = licentie_mapping.get(
                    row.get("licentievorm", "").lower().strip(),
                    Pakket.Licentievorm.ANDERS,
                )

                if not dry_run:
                    Pakket.objects.create(
                        legacy_id=legacy_id,
                        naam=row.get("naam", "Onbekend").strip(),
                        versie=row.get("versie", "").strip(),
                        status=Pakket.Status.ACTIEF,
                        beschrijving=row.get("beschrijving", "").strip(),
                        leverancier=leverancier,
                        licentievorm=licentie,
                        website_url=row.get("website", "").strip()[:200],
                    )
                self.stats["pakketten"]["created"] += 1
            except Exception as e:
                self.stats["pakketten"]["errors"] += 1
                self.errors.append(f"Pakket {legacy_id}: {e}")

    def _import_standaarden(self, filepath, dry_run):
        """Importeer standaarden en pakket-standaard koppelingen."""
        self.stdout.write(f"\nImporteer standaarden uit {filepath}...")
        rows = self._read_csv(filepath)

        type_mapping = {
            "verplicht": Standaard.Type.VERPLICHT,
            "aanbevolen": Standaard.Type.AANBEVOLEN,
        }

        for row in rows:
            naam = row.get("naam", "").strip()
            if not naam:
                self.stats["standaarden"]["skipped"] += 1
                continue

            try:
                standaard_type = type_mapping.get(
                    row.get("type", "").lower().strip(),
                    Standaard.Type.OPTIONEEL,
                )

                if not dry_run:
                    standaard, _ = Standaard.objects.get_or_create(
                        naam=naam,
                        defaults={
                            "type": standaard_type,
                            "versie": row.get("versie", "").strip(),
                            "beschrijving": row.get("beschrijving", "").strip(),
                            "forum_standaardisatie_url": row.get("url", "").strip()[:200],
                        },
                    )

                    # Koppel aan pakket indien van toepassing
                    pakket_id = row.get("pakket_guid", "").strip()
                    if pakket_id:
                        pakket = Pakket.objects.filter(legacy_id=pakket_id).first()
                        if pakket:
                            PakketStandaard.objects.get_or_create(
                                pakket=pakket,
                                standaard=standaard,
                                defaults={"ondersteund": True},
                            )

                self.stats["standaarden"]["created"] += 1
            except Exception as e:
                self.stats["standaarden"]["errors"] += 1
                self.errors.append(f"Standaard {naam}: {e}")

    def _import_pakketgebruik(self, filepath, dry_run):
        """Importeer pakketgebruik uit CSV."""
        self.stdout.write(f"\nImporteer pakketgebruik uit {filepath}...")
        rows = self._read_csv(filepath)

        for row in rows:
            try:
                pakket_id = row.get("pakket_guid", row.get("pakket_id", "")).strip()
                org_id = row.get("organisatie_guid", row.get("organisatie_id", "")).strip()

                if not pakket_id or not org_id:
                    self.stats["gebruik"]["skipped"] += 1
                    continue

                pakket = Pakket.objects.filter(legacy_id=pakket_id).first()
                organisatie = Organisatie.objects.filter(legacy_id=org_id).first()

                if not pakket or not organisatie:
                    self.stats["gebruik"]["skipped"] += 1
                    continue

                if PakketGebruik.objects.filter(pakket=pakket, organisatie=organisatie).exists():
                    self.stats["gebruik"]["skipped"] += 1
                    continue

                start_datum = None
                raw_datum = row.get("start_datum", "").strip()
                if raw_datum:
                    try:
                        start_datum = datetime.strptime(raw_datum, "%Y-%m-%d").date()
                    except ValueError:
                        pass

                if not dry_run:
                    PakketGebruik.objects.create(
                        pakket=pakket,
                        organisatie=organisatie,
                        status=PakketGebruik.Status.IN_GEBRUIK,
                        start_datum=start_datum,
                    )
                self.stats["gebruik"]["created"] += 1
            except Exception as e:
                self.stats["gebruik"]["errors"] += 1
                self.errors.append(f"Gebruik: {e}")

    def _import_koppelingen(self, filepath, dry_run):
        """Importeer koppelingen tussen pakketten."""
        self.stdout.write(f"\nImporteer koppelingen uit {filepath}...")
        rows = self._read_csv(filepath)

        for row in rows:
            try:
                van_pakket_id = row.get("van_pakket_guid", "").strip()
                naar_pakket_id = row.get("naar_pakket_guid", "").strip()
                org_id = row.get("organisatie_guid", "").strip()

                if not van_pakket_id or not naar_pakket_id or not org_id:
                    self.stats["koppelingen"]["skipped"] += 1
                    continue

                organisatie = Organisatie.objects.filter(legacy_id=org_id).first()
                van_pakket = Pakket.objects.filter(legacy_id=van_pakket_id).first()
                naar_pakket = Pakket.objects.filter(legacy_id=naar_pakket_id).first()

                if not organisatie or not van_pakket or not naar_pakket:
                    self.stats["koppelingen"]["skipped"] += 1
                    continue

                van_gebruik = PakketGebruik.objects.filter(
                    pakket=van_pakket, organisatie=organisatie
                ).first()
                naar_gebruik = PakketGebruik.objects.filter(
                    pakket=naar_pakket, organisatie=organisatie
                ).first()

                if not van_gebruik or not naar_gebruik:
                    self.stats["koppelingen"]["skipped"] += 1
                    continue

                if not dry_run:
                    Koppeling.objects.get_or_create(
                        van_pakket_gebruik=van_gebruik,
                        naar_pakket_gebruik=naar_gebruik,
                        defaults={
                            "type": row.get("type", "anders").strip() or "anders",
                            "beschrijving": row.get("beschrijving", "").strip(),
                        },
                    )
                self.stats["koppelingen"]["created"] += 1
            except Exception as e:
                self.stats["koppelingen"]["errors"] += 1
                self.errors.append(f"Koppeling: {e}")

    def _print_report(self):
        """Toon het migratierapport."""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("MIGRATIERAPPORT")
        self.stdout.write("=" * 60)

        for entity, counts in self.stats.items():
            self.stdout.write(f"\n  {entity.capitalize()}:")
            self.stdout.write(self.style.SUCCESS(f"    Aangemaakt: {counts['created']}"))
            if counts["skipped"]:
                self.stdout.write(f"    Overgeslagen: {counts['skipped']}")
            if counts["errors"]:
                self.stdout.write(self.style.ERROR(f"    Fouten: {counts['errors']}"))

        total_created = sum(c["created"] for c in self.stats.values())
        total_errors = sum(c["errors"] for c in self.stats.values())

        self.stdout.write(f"\n  Totaal aangemaakt: {total_created}")
        if total_errors:
            self.stdout.write(self.style.ERROR(f"  Totaal fouten: {total_errors}"))

        if self.errors:
            self.stdout.write(self.style.ERROR(f"\n  Foutdetails ({len(self.errors)}):"))
            for err in self.errors[:50]:
                self.stdout.write(f"    - {err}")
            if len(self.errors) > 50:
                self.stdout.write(f"    ... en {len(self.errors) - 50} meer")

        self.stdout.write("\n" + "=" * 60)
