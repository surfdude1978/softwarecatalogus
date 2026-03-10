"""
Management command: importeer leveranciers en pakketten uit de SWC-CSV-export.

Gebruik:
    python manage.py import_swc_csv /docs/leveranciers_pakketten_20260305_2008.csv
    python manage.py import_swc_csv /docs/leveranciers_pakketten_20260305_2008.csv --dry-run

Het CSV-bestand is semicolon-gescheiden (;) met aanhalingstekens voor velden
die newlines of puntkomma's bevatten. Exportformaat van softwarecatalogus.nl.

Per uniek Pakket ID wordt de meest relevante versie geselecteerd:
  prioriteit: In gebruik > In ontwikkeling > Teruggetrokken > Einde ondersteuning

Mappen naar Django-modellen:
  Leverancier Naam/ID  →  Organisatie (type=leverancier)
  Pakket Naam/ID       →  Pakket
  Referentiecomponenten UUID  →  PakketGemmaComponent (indien component bestaat)
"""

import csv
import io
from collections import defaultdict
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.architectuur.models import GemmaComponent, PakketGemmaComponent
from apps.organisaties.models import Organisatie
from apps.pakketten.models import Pakket


# Prioriteit voor versieselectie (hogere waarde = betere keuze)
VERSIE_PRIORITEIT = {
    "In gebruik": 4,
    "In ontwikkeling": 3,
    "Teruggetrokken": 2,
    "Einde ondersteuning": 1,
}

STATUS_MAP = {
    "In gebruik": Pakket.Status.ACTIEF,
    "In ontwikkeling": Pakket.Status.CONCEPT,
    "Teruggetrokken": Pakket.Status.INGETROKKEN,
    "Einde ondersteuning": Pakket.Status.VEROUDERD,
}


class Command(BaseCommand):
    help = "Importeer leveranciers en pakketten vanuit de SWC CSV-export"

    def add_arguments(self, parser):
        parser.add_argument("csv_pad", help="Pad naar het CSV-bestand")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simuleer de import zonder iets op te slaan",
        )
        parser.add_argument(
            "--encoding",
            default="utf-8-sig",
            help="Bestandscodering (standaard: utf-8-sig voor UTF-8 met BOM)",
        )

    def handle(self, *args, **options):
        csv_pad = options["csv_pad"]
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY-RUN modus — niets wordt opgeslagen\n"))

        # --- Lees CSV ---
        try:
            with open(csv_pad, encoding=options["encoding"], newline="") as f:
                inhoud = f.read()
        except FileNotFoundError:
            raise CommandError(f"Bestand niet gevonden: {csv_pad}")

        reader = csv.DictReader(io.StringIO(inhoud), delimiter=";", quotechar='"')
        rijen = list(reader)
        self.stdout.write(f"Gelezen: {len(rijen)} rijen\n")

        # --- Groepeer per Pakket ID ---
        pakket_groepen: dict[str, list[dict]] = defaultdict(list)
        for rij in rijen:
            pakket_id = rij.get("Pakket ID", "").strip()
            if pakket_id:
                pakket_groepen[pakket_id].append(rij)

        self.stdout.write(f"Unieke pakketten: {len(pakket_groepen)}\n")

        # --- Selecteer beste versie per pakket ---
        beste_rijen: list[dict] = []
        for pakket_id, versies in pakket_groepen.items():
            beste = max(
                versies,
                key=lambda r: (
                    VERSIE_PRIORITEIT.get(r.get("Pakketversie Status", "").strip(), 0),
                    _parse_datum(r.get("Mutatiedatum pakketversie", "")),
                ),
            )
            beste_rijen.append(beste)

        # --- Verzamel unieke leveranciers ---
        leverancier_map: dict[str, dict] = {}
        for rij in beste_rijen:
            lev_id = rij.get("Leverancier ID", "").strip()
            if lev_id and lev_id not in leverancier_map:
                leverancier_map[lev_id] = {
                    "naam": rij.get("Leverancier Naam", "").strip(),
                    "legacy_id": lev_id,
                }

        self.stdout.write(f"Unieke leveranciers: {len(leverancier_map)}\n\n")

        stats = {
            "leveranciers_aangemaakt": 0,
            "leveranciers_al_aanwezig": 0,
            "pakketten_aangemaakt": 0,
            "pakketten_al_aanwezig": 0,
            "gemma_koppelingen": 0,
            "gemma_niet_gevonden": 0,
            "fouten": 0,
        }

        with transaction.atomic():
            # --- Stap 1: Leveranciers aanmaken ---
            self.stdout.write("Leveranciers importeren...")
            org_cache: dict[str, Organisatie] = {}

            for lev_id, lev_data in leverancier_map.items():
                try:
                    org, aangemaakt = Organisatie.objects.get_or_create(
                        legacy_id=lev_id,
                        defaults={
                            "naam": lev_data["naam"],
                            "type": Organisatie.Type.LEVERANCIER,
                            "status": Organisatie.Status.ACTIEF,
                        },
                    )
                    org_cache[lev_id] = org
                    if aangemaakt:
                        stats["leveranciers_aangemaakt"] += 1
                    else:
                        stats["leveranciers_al_aanwezig"] += 1
                except Exception as exc:
                    self.stderr.write(f"  FOUT leverancier {lev_data['naam']}: {exc}")
                    stats["fouten"] += 1

            self.stdout.write(
                f"  Aangemaakt: {stats['leveranciers_aangemaakt']}, "
                f"al aanwezig: {stats['leveranciers_al_aanwezig']}\n"
            )

            # --- Stap 2: Pakketten aanmaken ---
            self.stdout.write("Pakketten importeren...")

            for rij in beste_rijen:
                pakket_id = rij.get("Pakket ID", "").strip()
                lev_id = rij.get("Leverancier ID", "").strip()
                org = org_cache.get(lev_id)

                if not org:
                    self.stderr.write(f"  OVERGESLAGEN: geen leverancier voor pakket {rij.get('Pakket Naam')}")
                    stats["fouten"] += 1
                    continue

                versie_status = rij.get("Pakketversie Status", "").strip()
                technologieen = rij.get("Pakketversie Ondersteunde technologieën", "")
                licentievorm = _bepaal_licentievorm(technologieen)
                website_url = rij.get("Pakket URL productpagina", "").strip()

                defaults = {
                    "naam": rij.get("Pakket Naam", "").strip(),
                    "versie": rij.get("Pakketversie Naam", "").strip(),
                    "beschrijving": rij.get("Pakket Beschrijving", "").strip(),
                    "status": STATUS_MAP.get(versie_status, Pakket.Status.VEROUDERD),
                    "leverancier": org,
                    "licentievorm": licentievorm,
                    "website_url": website_url if _is_geldige_url(website_url) else "",
                }

                try:
                    pakket, aangemaakt = Pakket.objects.get_or_create(
                        legacy_id=pakket_id,
                        defaults=defaults,
                    )
                    if aangemaakt:
                        stats["pakketten_aangemaakt"] += 1
                    else:
                        stats["pakketten_al_aanwezig"] += 1
                except Exception as exc:
                    self.stderr.write(f"  FOUT pakket {rij.get('Pakket Naam')}: {exc}")
                    stats["fouten"] += 1
                    continue

                # --- Stap 3: GEMMA-componenten koppelen ---
                uuids_str = rij.get("Referentiecomponenten leverancier UUID", "").strip()
                if uuids_str and aangemaakt:
                    for uuid_raw in uuids_str.split(","):
                        uuid = uuid_raw.strip()
                        if not uuid:
                            continue
                        try:
                            component = GemmaComponent.objects.get(archimate_id=uuid)
                            PakketGemmaComponent.objects.get_or_create(
                                pakket=pakket,
                                gemma_component=component,
                            )
                            stats["gemma_koppelingen"] += 1
                        except GemmaComponent.DoesNotExist:
                            stats["gemma_niet_gevonden"] += 1

            self.stdout.write(
                f"  Aangemaakt: {stats['pakketten_aangemaakt']}, "
                f"al aanwezig: {stats['pakketten_al_aanwezig']}\n"
            )

            if dry_run:
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING("\nDRY-RUN: alle wijzigingen teruggedraaid\n"))

        # --- Samenvatting ---
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("Import voltooid") if not dry_run else self.style.WARNING("Dry-run voltooid"))
        self.stdout.write(f"  Leveranciers aangemaakt : {stats['leveranciers_aangemaakt']}")
        self.stdout.write(f"  Leveranciers al aanwezig: {stats['leveranciers_al_aanwezig']}")
        self.stdout.write(f"  Pakketten aangemaakt    : {stats['pakketten_aangemaakt']}")
        self.stdout.write(f"  Pakketten al aanwezig   : {stats['pakketten_al_aanwezig']}")
        self.stdout.write(f"  GEMMA-koppelingen       : {stats['gemma_koppelingen']}")
        self.stdout.write(f"  GEMMA niet gevonden     : {stats['gemma_niet_gevonden']}")
        self.stdout.write(f"  Fouten                  : {stats['fouten']}")
        self.stdout.write("=" * 50)


def _bepaal_licentievorm(technologieen: str) -> str:
    """Bepaal licentievorm op basis van de opgegeven technologieën."""
    if "Software as a Service" in technologieen or "SAAS" in technologieen:
        return Pakket.Licentievorm.SAAS
    return Pakket.Licentievorm.COMMERCIEEL


def _is_geldige_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


def _parse_datum(datum_str: str) -> datetime:
    """Parseer dd-mm-yy of dd-mm-yyyy naar datetime voor sortering."""
    datum_str = datum_str.strip()
    for fmt in ("%d-%m-%y", "%d-%m-%Y"):
        try:
            return datetime.strptime(datum_str, fmt)
        except ValueError:
            continue
    return datetime.min
