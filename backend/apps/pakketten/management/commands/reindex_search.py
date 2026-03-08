"""Management command voor het herindexeren van Meilisearch."""
from django.core.management.base import BaseCommand

from apps.pakketten.search import reindex_all


class Command(BaseCommand):
    help = "Herindexeer alle pakketten in Meilisearch"

    def handle(self, *args, **options):
        self.stdout.write("Bezig met herindexeren van pakketten...")
        reindex_all()
        self.stdout.write(self.style.SUCCESS("Herindexering voltooid."))
