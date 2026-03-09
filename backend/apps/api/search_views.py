"""Zoek-endpoint dat Meilisearch gebruikt met ORM-fallback."""

import logging

from django.db.models import Count, Q
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pakketten.search import search_pakketten

logger = logging.getLogger(__name__)


def _orm_zoek(query: str, licentievorm: str | None, offset: int, limit: int) -> dict:
    """ORM-fallback wanneer Meilisearch niet beschikbaar is of geen resultaten geeft."""
    from apps.pakketten.models import Pakket

    qs = (
        Pakket.objects.filter(status="actief")
        .filter(Q(naam__icontains=query) | Q(beschrijving__icontains=query) | Q(leverancier__naam__icontains=query))
        .select_related("leverancier")
        .annotate(aantal_gebruikers_actief=Count("pakketgebruik", filter=Q(pakketgebruik__status="in_gebruik")))
    )

    if licentievorm:
        qs = qs.filter(licentievorm=licentievorm)

    totaal = qs.count()
    pagina = list(qs.order_by("naam")[offset : offset + limit])

    hits = [
        {
            "id": str(p.id),
            "naam": p.naam,
            "versie": p.versie or "",
            "status": p.status,
            "beschrijving": p.beschrijving or "",
            "leverancier_naam": p.leverancier.naam if p.leverancier else "",
            "licentievorm": p.licentievorm or "",
            "aantal_gebruikers": p.aantal_gebruikers_actief,
        }
        for p in pagina
    ]

    return {"hits": hits, "total": totaal, "offset": offset, "limit": limit}


class ZoekView(APIView):
    """
    Zoek in de softwarecatalogus via Meilisearch (met ORM-fallback).

    Query parameters:
    - q: zoekterm (verplicht)
    - licentievorm: filter op licentievorm
    - leverancier: filter op leverancier ID
    - standaard: filter op standaard ID
    - gemma_component: filter op GEMMA component ID
    - sort: sorteer op (naam:asc, naam:desc, populair, recent)
    - offset: paginatie offset (default 0)
    - limit: aantal resultaten (default 25, max 100)
    """

    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get("q", "")
        if not query:
            return Response(
                {"detail": "Zoekterm (q) is verplicht."},
                status=400,
            )

        licentievorm = request.query_params.get("licentievorm")
        leverancier = request.query_params.get("leverancier")
        standaard = request.query_params.get("standaard")
        gemma_component = request.query_params.get("gemma_component")

        # Paginatie
        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
            limit = min(100, max(1, int(request.query_params.get("limit", 25))))
        except (ValueError, TypeError):
            offset, limit = 0, 25

        # Sorteer
        sort_param = request.query_params.get("sort")
        sort = None
        if sort_param:
            allowed_sorts = {
                "naam:asc": ["naam:asc"],
                "naam:desc": ["naam:desc"],
                "populair": ["aantal_gebruikers:desc"],
                "recent": ["aangemaakt_op:desc"],
            }
            sort = allowed_sorts.get(sort_param)

        # Bouw Meilisearch filters — publiek ziet alleen actieve pakketten
        filter_parts = ['status = "actief"']
        if licentievorm:
            filter_parts.append(f'licentievorm = "{licentievorm}"')
        if leverancier:
            filter_parts.append(f'leverancier_id = "{leverancier}"')
        if standaard:
            filter_parts.append(f'standaard_ids = "{standaard}"')
        if gemma_component:
            filter_parts.append(f'gemma_component_ids = "{gemma_component}"')

        meilisearch_filter = " AND ".join(filter_parts)

        # Probeer Meilisearch; val terug op ORM bij fout
        try:
            result = search_pakketten(
                query=query,
                filters=meilisearch_filter,
                sort=sort,
                offset=offset,
                limit=limit,
            )
        except Exception:
            logger.warning(
                "Meilisearch niet beschikbaar, ORM-fallback gebruikt voor query '%s'",
                query,
            )
            result = _orm_zoek(query, licentievorm, offset, limit)

        return Response(result)
