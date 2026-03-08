"""
Management command om TenderNed aanbestedingen te synchroniseren.

Gebruik:
    python manage.py sync_aanbestedingen
    python manage.py sync_aanbestedingen --dagen 60
    python manage.py sync_aanbestedingen --max 500
    python manage.py sync_aanbestedingen --demo   # Gebruik altijd demo-data
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Synchroniseer ICT-aanbestedingen vanuit TenderNed Open Data API."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dagen",
            type=int,
            default=30,
            help="Hoeveel dagen terug te zoeken (standaard: 30)",
        )
        parser.add_argument(
            "--max",
            type=int,
            default=200,
            help="Maximum aantal te verwerken aanbestedingen (standaard: 200)",
        )
        parser.add_argument(
            "--demo",
            action="store_true",
            help="Gebruik demo-data in plaats van de echte TenderNed API",
        )

    def handle(self, *args, **options):
        from apps.aanbestedingen.client import TenderNedClient
        from apps.aanbestedingen.tasks import sync_tenderned

        if options["demo"]:
            self.stdout.write("Demo-modus ingeschakeld — voorbeelddata gebruiken")

        self.stdout.write(
            f"Synchroniseren van aanbestedingen (laatste {options['dagen']} dagen, "
            f"max {options['max']})..."
        )

        # Direct uitvoeren (niet via Celery) zodat het synchron werkt in management command
        from apps.aanbestedingen.client import TenderNedClient
        import django
        from django.conf import settings

        # Tijdelijk demo-mode overschrijven indien gevraagd
        if options["demo"]:
            original_setting = getattr(settings, "TENDERNED_DEMO_MODE", True)
            settings.TENDERNED_DEMO_MODE = True

        try:
            resultaat = sync_tenderned(
                dagen_terug=options["dagen"],
                max_resultaten=options["max"],
            )
        finally:
            if options["demo"]:
                settings.TENDERNED_DEMO_MODE = original_setting

        self.stdout.write(self.style.SUCCESS(
            f"✓ Sync klaar: {resultaat['aangemaakt']} aangemaakt, "
            f"{resultaat['bijgewerkt']} bijgewerkt, "
            f"{resultaat['fouten']} fouten "
            f"({resultaat['duur_seconden']}s)"
        ))
