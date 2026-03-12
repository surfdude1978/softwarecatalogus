# SPDX-License-Identifier: EUPL-1.2
"""
MCP Server voor de Softwarecatalogus.

Maakt de Softwarecatalogus API beschikbaar als tools voor AI-assistenten.
Doorzoek softwarepakketten, organisaties, standaarden, GEMMA-componenten
en ICT-aanbestedingen van Nederlandse gemeenten.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .api_client import client

mcp = FastMCP(
    "Softwarecatalogus",
    instructions=(
        "MCP-server voor de Nederlandse Softwarecatalogus — "
        "zoek en raadpleeg softwarepakketten, organisaties, "
        "standaarden, GEMMA-componenten en ICT-aanbestedingen "
        "voor gemeenten."
    ),
)


# ---------------------------------------------------------------------------
# 1. Zoeken
# ---------------------------------------------------------------------------


@mcp.tool()
async def zoek_pakketten(
    query: str,
    licentievorm: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
) -> dict:
    """Zoek softwarepakketten via full-text search in de catalogus.

    Doorzoekt pakketnamen, beschrijvingen, leveranciers, GEMMA-componenten
    en standaarden. Resultaten zijn gesorteerd op relevantie.

    Args:
        query: Zoekterm (verplicht), bijv. "burgerzaken" of "zaaksysteem".
        licentievorm: Filter op licentie — commercieel, open_source, saas of anders.
        sort: Sortering — naam:asc, naam:desc, populair of recent.
        offset: Startpositie voor paginatie (standaard 0).
        limit: Max aantal resultaten (standaard 25, max 100).
    """
    return await client.get(
        "/api/v1/zoek/",
        params={
            "q": query,
            "licentievorm": licentievorm,
            "sort": sort,
            "offset": offset,
            "limit": limit,
        },
    )


# ---------------------------------------------------------------------------
# 2. Pakketten
# ---------------------------------------------------------------------------


@mcp.tool()
async def lijst_pakketten(
    status: str | None = None,
    licentievorm: str | None = None,
    leverancier: str | None = None,
    gemma_componenten: str | None = None,
    standaarden: str | None = None,
    search: str | None = None,
    ordering: str | None = None,
    page: int | None = None,
) -> dict:
    """Bladeren en filteren van softwarepakketten in de catalogus.

    Gebruik deze tool om pakketten te bekijken zonder full-text search,
    of om te filteren op specifieke eigenschappen.

    Args:
        status: Filter op status — concept, actief, verouderd of ingetrokken.
        licentievorm: Filter — commercieel, open_source, saas of anders.
        leverancier: Filter op leverancier-UUID.
        gemma_componenten: Filter op GEMMA-component UUID.
        standaarden: Filter op standaard-UUID.
        search: Eenvoudige tekst-zoekfilter op naam/beschrijving.
        ordering: Sortering — naam, -naam, aangemaakt_op, -aangemaakt_op, aantal_gebruikers.
        page: Paginanummer (standaard 1).
    """
    return await client.get(
        "/api/v1/pakketten/",
        params={
            "status": status,
            "licentievorm": licentievorm,
            "leverancier": leverancier,
            "gemma_componenten": gemma_componenten,
            "standaarden": standaarden,
            "search": search,
            "ordering": ordering,
            "page": page,
        },
    )


@mcp.tool()
async def pakket_detail(pakket_id: str) -> dict:
    """Haal de volledige details op van een softwarepakket.

    Bevat: beschrijving, leverancier, ondersteunde standaarden,
    GEMMA-componenten, gebruikende organisaties en gerelateerde documenten.

    Args:
        pakket_id: UUID van het pakket.
    """
    return await client.get(f"/api/v1/pakketten/{pakket_id}/")


# ---------------------------------------------------------------------------
# 3. Organisaties
# ---------------------------------------------------------------------------


@mcp.tool()
async def lijst_organisaties(
    type: str | None = None,
    search: str | None = None,
    ordering: str | None = None,
    page: int | None = None,
) -> dict:
    """Zoek en filter organisaties (gemeenten, leveranciers, samenwerkingsverbanden).

    Args:
        type: Filter op type — gemeente, leverancier, samenwerkingsverband of overig.
        search: Zoek op naam of OIN.
        ordering: Sortering — naam, -naam.
        page: Paginanummer.
    """
    return await client.get(
        "/api/v1/organisaties/",
        params={
            "type": type,
            "search": search,
            "ordering": ordering,
            "page": page,
        },
    )


@mcp.tool()
async def organisatie_detail(organisatie_id: str) -> dict:
    """Haal de volledige details van een organisatie op.

    Bevat: contactpersonen, aantal pakketten, type en status.

    Args:
        organisatie_id: UUID van de organisatie.
    """
    return await client.get(f"/api/v1/organisaties/{organisatie_id}/")


# ---------------------------------------------------------------------------
# 4. GEMMA Architectuur
# ---------------------------------------------------------------------------


@mcp.tool()
async def lijst_gemma_componenten(
    type: str | None = None,
    search: str | None = None,
    parent__isnull: bool | None = None,
) -> list:
    """Lijst van GEMMA-referentiecomponenten uit de gemeentelijke architectuur.

    GEMMA is de referentiearchitectuur voor Nederlandse gemeenten (ArchiMate).
    Componenten zijn bijv. "Zaaksysteem", "Burgerzakenmodule", "BRP-koppeling".

    Args:
        type: Filter op type — applicatiecomponent, applicatieservice, etc.
        search: Zoek op naam of ArchiMate-ID.
        parent__isnull: True voor alleen root-componenten, False voor kinderen.
    """
    return await client.get(
        "/api/v1/gemma/componenten/",
        params={
            "type": type,
            "search": search,
            "parent__isnull": parent__isnull,
        },
    )


@mcp.tool()
async def gemma_kaart(organisatie: str | None = None) -> dict:
    """Haal de volledige GEMMA-architectuurkaart op.

    Retourneert een hierarchische boomstructuur van GEMMA-componenten
    met per component de bijbehorende softwarepakketten.
    Ideaal om te zien welke pakketten gemeenten gebruiken per
    GEMMA-referentiecomponent.

    Args:
        organisatie: Optioneel UUID van een organisatie om alleen hun
            pakketten te tonen. Gebruik lijst_organisaties om het UUID
            van een gemeente te vinden.
    """
    return await client.get(
        "/api/v1/gemma/kaart/",
        params={"organisatie": organisatie},
    )


# ---------------------------------------------------------------------------
# 5. Standaarden
# ---------------------------------------------------------------------------


@mcp.tool()
async def lijst_standaarden(
    type: str | None = None,
    search: str | None = None,
) -> list:
    """Lijst van standaarden uit het Forum Standaardisatie.

    Standaarden kunnen verplicht, aanbevolen of optioneel zijn voor
    Nederlandse overheidsorganisaties. Pakketten in de catalogus
    registreren welke standaarden ze ondersteunen.

    Args:
        type: Filter — verplicht, aanbevolen of optioneel.
        search: Zoek op naam.
    """
    return await client.get(
        "/api/v1/standaarden/",
        params={"type": type, "search": search},
    )


# ---------------------------------------------------------------------------
# 6. Aanbestedingen
# ---------------------------------------------------------------------------


@mcp.tool()
async def zoek_aanbestedingen(
    search: str | None = None,
    type: str | None = None,
    status: str | None = None,
    gemeente: str | None = None,
    publicatiedatum_vanaf: str | None = None,
    publicatiedatum_tot: str | None = None,
    page: int | None = None,
) -> dict:
    """Zoek ICT-aanbestedingen van gemeenten (TenderNed).

    Vindt relevante Europese en nationale aanbestedingen op het gebied
    van ICT en software voor de overheid.

    Args:
        search: Zoekterm in titel of beschrijving.
        type: Filter — europees of nationaal.
        status: Filter op aanbestedingsstatus.
        gemeente: Filter op gemeentenaam (fuzzy matching).
        publicatiedatum_vanaf: Vanaf-datum (YYYY-MM-DD).
        publicatiedatum_tot: Tot-datum (YYYY-MM-DD).
        page: Paginanummer.
    """
    return await client.get(
        "/api/v1/aanbestedingen/",
        params={
            "search": search,
            "type": type,
            "status": status,
            "gemeente": gemeente,
            "publicatiedatum__gte": publicatiedatum_vanaf,
            "publicatiedatum__lte": publicatiedatum_tot,
            "page": page,
        },
    )


@mcp.tool()
async def aanbesteding_detail(aanbesteding_id: str) -> dict:
    """Haal de volledige details van een ICT-aanbesteding op.

    Bevat: aanbestedende dienst, GEMMA-componenten, relevante pakketten,
    CPV-codes, publicatiedatum en status.

    Args:
        aanbesteding_id: UUID van de aanbesteding.
    """
    return await client.get(f"/api/v1/aanbestedingen/{aanbesteding_id}/")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
