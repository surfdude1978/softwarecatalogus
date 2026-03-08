"""Signals voor het synchroniseren van pakketten met Meilisearch."""
import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Pakket

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Pakket)
def pakket_saved(sender, instance, **kwargs):
    """Synchroniseer pakket naar Meilisearch bij opslaan."""
    try:
        from .search import index_pakket
        index_pakket(instance)
    except Exception:
        logger.exception("Fout bij Meilisearch sync voor pakket %s", instance.id)


@receiver(post_delete, sender=Pakket)
def pakket_deleted(sender, instance, **kwargs):
    """Verwijder pakket uit Meilisearch bij verwijdering."""
    try:
        from .search import remove_pakket
        remove_pakket(instance.id)
    except Exception:
        logger.exception("Fout bij Meilisearch verwijdering voor pakket %s", instance.id)
