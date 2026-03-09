"""Meilisearch integratie voor pakketten."""

import logging

import meilisearch
from django.conf import settings

logger = logging.getLogger(__name__)

_client = None


def get_client():
    """Lazy Meilisearch client initialisatie."""
    global _client
    if _client is None:
        _client = meilisearch.Client(
            settings.MEILISEARCH_URL,
            settings.MEILISEARCH_API_KEY,
        )
    return _client


def get_pakketten_index():
    """Haal de pakketten index op, maak aan indien nodig."""
    client = get_client()
    index = client.index("pakketten")
    return index


def configure_index():
    """Configureer de Meilisearch pakketten index."""
    try:
        client = get_client()
        client.create_index("pakketten", {"primaryKey": "id"})
    except meilisearch.errors.MeilisearchApiError:
        pass  # Index bestaat al

    index = get_pakketten_index()
    index.update_searchable_attributes(
        [
            "naam",
            "beschrijving",
            "leverancier_naam",
            "gemma_componenten",
            "standaarden",
        ]
    )
    index.update_filterable_attributes(
        [
            "status",
            "licentievorm",
            "leverancier_id",
            "gemma_component_ids",
            "standaard_ids",
        ]
    )
    index.update_sortable_attributes(
        [
            "naam",
            "aangemaakt_op",
            "aantal_gebruikers",
        ]
    )
    logger.info("Meilisearch pakketten index geconfigureerd.")


def pakket_to_document(pakket):
    """Converteer een Pakket model naar een Meilisearch document."""
    return {
        "id": str(pakket.id),
        "naam": pakket.naam,
        "versie": pakket.versie,
        "status": pakket.status,
        "beschrijving": pakket.beschrijving,
        "licentievorm": pakket.licentievorm,
        "leverancier_id": str(pakket.leverancier_id),
        "leverancier_naam": pakket.leverancier.naam if pakket.leverancier else "",
        "website_url": pakket.website_url,
        "gemma_componenten": [c.naam for c in pakket.gemma_componenten.all()],
        "gemma_component_ids": [str(c.id) for c in pakket.gemma_componenten.all()],
        "standaarden": [s.naam for s in pakket.standaarden.all()],
        "standaard_ids": [str(s.id) for s in pakket.standaarden.all()],
        "aantal_gebruikers": pakket.pakketgebruik_set.filter(status="in_gebruik").count(),
        "aangemaakt_op": pakket.aangemaakt_op.isoformat() if pakket.aangemaakt_op else None,
    }


def index_pakket(pakket):
    """Indexeer of update een enkel pakket in Meilisearch."""
    try:
        index = get_pakketten_index()
        doc = pakket_to_document(pakket)
        index.add_documents([doc])
    except Exception:
        logger.exception("Fout bij indexeren pakket %s", pakket.id)


def remove_pakket(pakket_id):
    """Verwijder een pakket uit de Meilisearch index."""
    try:
        index = get_pakketten_index()
        index.delete_document(str(pakket_id))
    except Exception:
        logger.exception("Fout bij verwijderen pakket %s uit index", pakket_id)


def search_pakketten(query, filters=None, sort=None, offset=0, limit=25):
    """
    Zoek pakketten via Meilisearch.

    Gooit een uitzondering als Meilisearch niet beschikbaar is of de index
    niet bestaat — de aanroeper (search_views.py) vangt dit op en gebruikt
    een ORM-fallback.
    """
    index = get_pakketten_index()
    search_params = {
        "offset": offset,
        "limit": limit,
        "attributesToRetrieve": [
            "id",
            "naam",
            "versie",
            "status",
            "beschrijving",
            "leverancier_naam",
            "licentievorm",
            "aantal_gebruikers",
        ],
    }
    if filters:
        search_params["filter"] = filters
    if sort:
        search_params["sort"] = sort

    result = index.search(query, search_params)
    return {
        "hits": result["hits"],
        "total": result["estimatedTotalHits"],
        "offset": offset,
        "limit": limit,
    }


def reindex_all():
    """Herindexeer alle actieve pakketten."""
    from apps.pakketten.models import Pakket

    configure_index()
    pakketten = (
        Pakket.objects.filter(status__in=["actief", "concept"])
        .select_related("leverancier")
        .prefetch_related("gemma_componenten", "standaarden")
    )

    documents = [pakket_to_document(p) for p in pakketten]
    if documents:
        index = get_pakketten_index()
        # Batch toevoegen (max 10000 per batch)
        for i in range(0, len(documents), 10000):
            batch = documents[i : i + 10000]
            index.add_documents(batch)
    logger.info("Herindexering voltooid: %d pakketten", len(documents))
