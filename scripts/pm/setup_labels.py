#!/usr/bin/env python3
"""
GitHub Labels instellen voor Softwarecatalogus
===============================================
Eenmalig uitvoeren om alle benodigde labels aan te maken.

Gebruik:
  GITHUB_TOKEN=... python setup_labels.py --repo surfdude1978/softwarecatalogus
"""

import argparse
import os
import sys

import requests


LABELS = [
    # --- Prioriteit ---
    {"name": "priority:critical", "color": "d73a4a", "description": "Blokkerend — moet onmiddellijk opgelost worden"},
    {"name": "priority:high",     "color": "e4e669", "description": "Hoge prioriteit — oppakken in huidige sprint"},
    {"name": "priority:medium",   "color": "0075ca", "description": "Gemiddelde prioriteit — plannen voor komende sprint"},
    {"name": "priority:low",      "color": "cfd3d7", "description": "Lage prioriteit — kan wachten"},

    # --- Type ---
    {"name": "type:bug",          "color": "d73a4a", "description": "Iets werkt niet zoals verwacht"},
    {"name": "type:feature",      "color": "a2eeef", "description": "Nieuwe functionaliteit"},
    {"name": "type:enhancement",  "color": "84b6eb", "description": "Verbetering van bestaande functionaliteit"},
    {"name": "type:docs",         "color": "fef2c0", "description": "Documentatie aanpassing"},
    {"name": "type:infra",        "color": "e4e669", "description": "Infrastructuur / DevOps"},
    {"name": "type:question",     "color": "d876e3", "description": "Vraag of onduidelijkheid"},

    # --- Scope ---
    {"name": "scope:eis",         "color": "0e8a16", "description": "Functionele eis (MVP — verplicht)"},
    {"name": "scope:wens",        "color": "fbca04", "description": "Functionele wens (nice-to-have)"},
    {"name": "scope:intern",      "color": "bfd4f2", "description": "Interne technische taak"},

    # --- Ontwikkelfasen ---
    {"name": "fase-1",            "color": "1d76db", "description": "Fase 1: Fundament (Docker, auth, datamodel)"},
    {"name": "fase-2",            "color": "0052cc", "description": "Fase 2: Kernfunctionaliteiten (catalogus, registratie)"},
    {"name": "fase-3",            "color": "003d8a", "description": "Fase 3: Geavanceerde features (GEMMA, export)"},
    {"name": "fase-4",            "color": "002a5e", "description": "Fase 4: Beheer en Admin"},
    {"name": "fase-5",            "color": "001830", "description": "Fase 5: Kwaliteit en Productie"},

    # --- Grootte/Complexiteit ---
    {"name": "size:small",        "color": "c2e0c6", "description": "Klein — minder dan 1 dag"},
    {"name": "size:medium",       "color": "fef2c0", "description": "Gemiddeld — 1 tot 3 dagen"},
    {"name": "size:large",        "color": "f9d0c4", "description": "Groot — 3 tot 5 dagen"},
    {"name": "size:epic",         "color": "d73a4a", "description": "Epic — meerdere weken, opsplitsen aanbevolen"},

    # --- Componenten ---
    {"name": "component:backend",      "color": "e4e669", "description": "Django backend"},
    {"name": "component:frontend",     "color": "84b6eb", "description": "Next.js frontend"},
    {"name": "component:api",          "color": "a2eeef", "description": "REST API / DRF"},
    {"name": "component:auth",         "color": "bfd4f2", "description": "Authenticatie & autorisatie (2FA)"},
    {"name": "component:gemma",        "color": "0075ca", "description": "GEMMA ArchiMate integratie"},
    {"name": "component:zoeken",       "color": "c5def5", "description": "Meilisearch zoekfunctionaliteit"},
    {"name": "component:export",       "color": "fef2c0", "description": "Export (CSV/Excel/AMEFF)"},
    {"name": "component:documenten",   "color": "f9d0c4", "description": "Document uploads en beheer"},
    {"name": "component:organisaties", "color": "c2e0c6", "description": "Organisatiebeheer"},
    {"name": "component:pakketten",    "color": "e4e669", "description": "Pakket(gebruik) beheer"},
    {"name": "component:infra",        "color": "bfd4f2", "description": "Docker / Kubernetes / CI/CD"},

    # --- Automatisering ---
    {"name": "auto:implement",    "color": "0e8a16", "description": "🤖 Kan automatisch geïmplementeerd worden via Claude Code"},
    {"name": "auto:in-progress",  "color": "fbca04", "description": "🤖 Claude Code is bezig met implementatie"},
    {"name": "auto:done",         "color": "84b6eb", "description": "🤖 Automatisch geïmplementeerd — review vereist"},

    # --- Status ---
    {"name": "status:needs-info", "color": "d876e3", "description": "Meer informatie nodig van de indiener"},
    {"name": "status:blocked",    "color": "d73a4a", "description": "Geblokkeerd door ander issue of externe factor"},
    {"name": "status:ready",      "color": "0e8a16", "description": "Klaar voor implementatie"},
    {"name": "status:in-review",  "color": "fbca04", "description": "Pull request in review"},
    {"name": "status:wontfix",    "color": "ffffff", "description": "Wordt niet geïmplementeerd"},
]


def maak_of_update_label(repo: str, label: dict, token: str) -> str:
    """Maak een label aan of update het als het al bestaat. Geeft 'created', 'updated' of 'error' terug."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Probeer te maken
    url = f"https://api.github.com/repos/{repo}/labels"
    resp = requests.post(url, json=label, headers=headers, timeout=30)

    if resp.status_code == 201:
        return "created"
    elif resp.status_code == 422:
        # Al bestaand — update het
        update_url = f"https://api.github.com/repos/{repo}/labels/{requests.utils.quote(label['name'])}"
        resp2 = requests.patch(update_url, json=label, headers=headers, timeout=30)
        if resp2.status_code == 200:
            return "updated"
        else:
            print(f"  Fout bij updaten: {resp2.status_code} {resp2.text}", file=sys.stderr)
            return "error"
    else:
        print(f"  Fout bij aanmaken: {resp.status_code} {resp.text}", file=sys.stderr)
        return "error"


def main():
    parser = argparse.ArgumentParser(description="GitHub labels instellen")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("FOUT: GITHUB_TOKEN omgevingsvariabele niet ingesteld", file=sys.stderr)
        sys.exit(1)
    if not args.repo:
        print("FOUT: --repo of GITHUB_REPOSITORY niet ingesteld", file=sys.stderr)
        sys.exit(1)

    print(f"Labels instellen voor repository: {args.repo}")
    print(f"Totaal aantal labels: {len(LABELS)}\n")

    gemaakt = updated = fouten = 0

    for label in LABELS:
        status = maak_of_update_label(args.repo, label, token)
        icon = {"created": "✅", "updated": "🔄", "error": "❌"}[status]
        print(f"  {icon} {label['name']}")
        if status == "created":
            gemaakt += 1
        elif status == "updated":
            updated += 1
        else:
            fouten += 1

    print(f"\nKlaar: {gemaakt} aangemaakt, {updated} bijgewerkt, {fouten} fouten")


if __name__ == "__main__":
    main()
