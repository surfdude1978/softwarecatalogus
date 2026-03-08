"""Zoek-endpoint dat Meilisearch gebruikt."""
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pakketten.search import search_pakketten


class ZoekView(APIView):
    """
    Zoek in de softwarecatalogus via Meilisearch.

    Query parameters:
    - q: zoekterm (verplicht)
    - licentievorm: filter op licentievorm
    - leverancier: filter op leverancier ID
    - standaard: filter op standaard ID
    - gemma_component: filter op GEMMA component ID
    - sort: sorteer op (naam:asc, naam:desc, aantal_gebruikers:desc)
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

        # Bouw filters
        filter_parts = ['status = "actief" OR status = "concept"']

        licentievorm = request.query_params.get("licentievorm")
        if licentievorm:
            filter_parts.append(f'licentievorm = "{licentievorm}"')

        leverancier = request.query_params.get("leverancier")
        if leverancier:
            filter_parts.append(f'leverancier_id = "{leverancier}"')

        standaard = request.query_params.get("standaard")
        if standaard:
            filter_parts.append(f'standaard_ids = "{standaard}"')

        gemma_component = request.query_params.get("gemma_component")
        if gemma_component:
            filter_parts.append(f'gemma_component_ids = "{gemma_component}"')

        filters = " AND ".join(filter_parts) if filter_parts else None

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

        # Paginatie
        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
            limit = min(100, max(1, int(request.query_params.get("limit", 25))))
        except (ValueError, TypeError):
            offset, limit = 0, 25

        result = search_pakketten(
            query=query,
            filters=filters,
            sort=sort,
            offset=offset,
            limit=limit,
        )

        return Response(result)
