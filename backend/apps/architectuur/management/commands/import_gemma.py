"""Management command voor het importeren van GEMMA componenten uit AMEFF."""
from django.core.management.base import BaseCommand, CommandError

from apps.architectuur.ameff_import import import_ameff


class Command(BaseCommand):
    help = "Importeer GEMMA componenten uit een AMEFF (ArchiMate Exchange) bestand"

    def add_arguments(self, parser):
        parser.add_argument("bestand", type=str, help="Pad naar het AMEFF XML-bestand")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Voer geen database wijzigingen door, toon alleen wat er zou gebeuren",
        )

    def handle(self, *args, **options):
        bestand_pad = options["bestand"]
        dry_run = options["dry_run"]

        try:
            with open(bestand_pad, "rb") as f:
                content = f.read()
        except FileNotFoundError:
            raise CommandError(f"Bestand niet gevonden: {bestand_pad}")

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — geen wijzigingen worden opgeslagen"))

        stats = import_ameff(content, dry_run=dry_run)

        self.stdout.write(f"\nResultaat:")
        self.stdout.write(f"  Elementen gevonden:  {stats['elements_found']}")
        self.stdout.write(f"  Relaties gevonden:   {stats['relationships_found']}")
        self.stdout.write(self.style.SUCCESS(f"  Aangemaakt:          {stats['created']}"))
        self.stdout.write(self.style.SUCCESS(f"  Bijgewerkt:          {stats['updated']}"))

        if stats["conflicts"]:
            self.stdout.write(self.style.WARNING(f"\n  Conflicten ({len(stats['conflicts'])}):"))
            for conflict in stats["conflicts"]:
                self.stdout.write(
                    f"    {conflict['archimate_id']}: "
                    f"'{conflict['old_name']}' -> '{conflict['new_name']}'"
                )
