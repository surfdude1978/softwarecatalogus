#!/usr/bin/env python3
"""
AI Product Manager — GitHub Issue Triage
=========================================
Analyseert nieuwe GitHub issues en voert automatisch triage uit:
  - Prioriteit bepalen (kritiek / hoog / gemiddeld / laag)
  - Type classificeren (bug / feature / enhancement / docs / infra)
  - Componenten identificeren (backend / frontend / api / auth / gemma / etc.)
  - Fase koppelen aan het OTAP-ontwikkelplan
  - Acceptatiecriteria opstellen
  - Bepalen of het issue automatisch geïmplementeerd kan worden

Gebruik:
  ANTHROPIC_API_KEY=... GITHUB_TOKEN=... python triage_issue.py \
    --repo surfdude1978/softwarecatalogus \
    --issue 42

Of via omgevingsvariabelen (GitHub Actions):
  ISSUE_NUMBER, REPO, ISSUE_TITLE, ISSUE_BODY worden automatisch ingesteld.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Literal

import anthropic
import requests
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Datamodellen
# ---------------------------------------------------------------------------

class IssueTriage(BaseModel):
    """Gestructureerde triageuitkomst van de AI-PM."""

    prioriteit: Literal["kritiek", "hoog", "gemiddeld", "laag"] = Field(
        description="Prioriteit op basis van impact, urgentie en MVP-vereisten"
    )
    type: Literal["bug", "feature", "enhancement", "docs", "infra", "vraag"] = Field(
        description="Type issue"
    )
    componenten: list[str] = Field(
        description="Betrokken componenten: backend, frontend, api, auth, gemma, zoeken, export, documenten, organisaties, pakketten, infra"
    )
    fase: Literal["fase-1", "fase-2", "fase-3", "fase-4", "fase-5"] | None = Field(
        description="Ontwikkelfase (uit CLAUDE.md) of null als niet van toepassing"
    )
    eis_of_wens: Literal["eis", "wens", "intern"] = Field(
        description="Is dit een functionele eis (EIS), functionele wens (nice-to-have), of interne technische taak"
    )
    complexiteit: Literal["klein", "gemiddeld", "groot", "epic"] = Field(
        description="Klein=<1 dag, Gemiddeld=1-3 dagen, Groot=3-5 dagen, Epic=meerdere weken"
    )
    auto_implementeerbaar: bool = Field(
        description="True als het issue klein genoeg is om volledig automatisch te implementeren via Claude Code"
    )
    samenvatting: str = Field(
        description="Beknopte samenvatting van het issue in 1-2 zinnen (Nederlands)"
    )
    acceptatiecriteria: list[str] = Field(
        description="Concrete, testbare acceptatiecriteria (Given/When/Then of bullet points)"
    )
    technische_aanpak: str = Field(
        description="Beknopte technische aanpak: welke bestanden/modules worden geraakt"
    )
    rationale: str = Field(
        description="Motivatie voor de gekozen prioriteit en aanpak (1-3 zinnen)"
    )
    gerelateerde_eisen: list[str] = Field(
        description="Gerelateerde functionele eisen uit CLAUDE.md, bijv. ['EIS-1: Aanbod Raadplegen', 'EIS-12: API']"
    )
    risicos: list[str] = Field(
        default_factory=list,
        description="Technische of functionele risico's (optioneel)"
    )


# ---------------------------------------------------------------------------
# Hulpfuncties
# ---------------------------------------------------------------------------

def laad_project_context() -> str:
    """Laad CLAUDE.md als projectcontext voor de AI."""
    claude_md = Path(__file__).parent.parent.parent / "CLAUDE.md"
    if claude_md.exists():
        return claude_md.read_text(encoding="utf-8")
    return ""


def haal_issue_op(repo: str, issue_number: int, token: str) -> dict:
    """Haal issue-details op via GitHub API."""
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def haal_comments_op(repo: str, issue_number: int, token: str) -> list[dict]:
    """Haal bestaande comments op om dubbele triage te voorkomen."""
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def is_al_getriageerd(comments: list[dict]) -> bool:
    """Controleer of het issue al getriageerd is door de PM-bot."""
    for comment in comments:
        if "<!-- pm-triage-bot -->" in comment.get("body", ""):
            return True
    return False


def voeg_labels_toe(repo: str, issue_number: int, labels: list[str], token: str) -> None:
    """Voeg labels toe aan een issue."""
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/labels"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    resp = requests.post(url, json={"labels": labels}, headers=headers, timeout=30)
    if resp.status_code not in (200, 201):
        print(f"Waarschuwing: labels toevoegen mislukt: {resp.status_code} {resp.text}", file=sys.stderr)


def plaats_comment(repo: str, issue_number: int, body: str, token: str) -> None:
    """Plaats een comment op een issue."""
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    resp = requests.post(url, json={"body": body}, headers=headers, timeout=30)
    resp.raise_for_status()


def triage_naar_labels(triage: IssueTriage) -> list[str]:
    """Vertaal triageresultaat naar GitHub labels."""
    labels = []

    # Prioriteit
    prioriteit_map = {
        "kritiek": "priority:critical",
        "hoog": "priority:high",
        "gemiddeld": "priority:medium",
        "laag": "priority:low",
    }
    labels.append(prioriteit_map[triage.prioriteit])

    # Type
    type_map = {
        "bug": "type:bug",
        "feature": "type:feature",
        "enhancement": "type:enhancement",
        "docs": "type:docs",
        "infra": "type:infra",
        "vraag": "type:question",
    }
    labels.append(type_map[triage.type])

    # Eis/wens
    eis_map = {
        "eis": "scope:eis",
        "wens": "scope:wens",
        "intern": "scope:intern",
    }
    labels.append(eis_map[triage.eis_of_wens])

    # Fase
    if triage.fase:
        labels.append(triage.fase)

    # Complexiteit
    complexiteit_map = {
        "klein": "size:small",
        "gemiddeld": "size:medium",
        "groot": "size:large",
        "epic": "size:epic",
    }
    labels.append(complexiteit_map[triage.complexiteit])

    # Auto-implementeerbaar
    if triage.auto_implementeerbaar:
        labels.append("auto:implement")

    # Componenten
    geldige_componenten = {
        "backend", "frontend", "api", "auth", "gemma",
        "zoeken", "export", "documenten", "organisaties", "pakketten", "infra"
    }
    for comp in triage.componenten:
        if comp.lower() in geldige_componenten:
            labels.append(f"component:{comp.lower()}")

    return labels


def maak_triage_comment(issue: dict, triage: IssueTriage) -> str:
    """Maak een geformatteerde triage-comment aan."""
    prioriteit_emoji = {
        "kritiek": "🔴",
        "hoog": "🟠",
        "gemiddeld": "🟡",
        "laag": "🟢",
    }
    type_emoji = {
        "bug": "🐛",
        "feature": "✨",
        "enhancement": "🔧",
        "docs": "📝",
        "infra": "🏗️",
        "vraag": "❓",
    }
    complexiteit_emoji = {
        "klein": "S",
        "gemiddeld": "M",
        "groot": "L",
        "epic": "XL",
    }

    ac_lijst = "\n".join(f"- [ ] {ac}" for ac in triage.acceptatiecriteria)
    eisen_lijst = "\n".join(f"- {e}" for e in triage.gerelateerde_eisen) if triage.gerelateerde_eisen else "_Geen directe koppeling_"
    risicos_sectie = ""
    if triage.risicos:
        risicos_lijst = "\n".join(f"- ⚠️ {r}" for r in triage.risicos)
        risicos_sectie = f"\n### ⚠️ Risico's\n{risicos_lijst}\n"

    auto_sectie = ""
    if triage.auto_implementeerbaar:
        auto_sectie = "\n> 🤖 **Auto-implementatie beschikbaar** — Voeg label `auto:implement` toe om Claude Code dit automatisch te laten implementeren.\n"

    return f"""<!-- pm-triage-bot -->
## 🤖 AI Product Manager — Triage

{prioriteit_emoji[triage.prioriteit]} **Prioriteit:** {triage.prioriteit.capitalize()} &nbsp;|&nbsp; \
{type_emoji[triage.type]} **Type:** {triage.type.capitalize()} &nbsp;|&nbsp; \
📏 **Complexiteit:** [{complexiteit_emoji[triage.complexiteit]}] {triage.complexiteit.capitalize()} &nbsp;|&nbsp; \
🏷️ **Scope:** {triage.eis_of_wens.upper()}

### 📋 Samenvatting
{triage.samenvatting}

### ✅ Acceptatiecriteria
{ac_lijst}

### 🔧 Technische aanpak
{triage.technische_aanpak}

### 🗺️ Gerelateerde eisen
{eisen_lijst}
{risicos_sectie}{auto_sectie}
### 💭 Toelichting prioriteit
{triage.rationale}

---
<sub>🤖 Automatisch gegenereerd door de AI Product Manager | Model: claude-opus-4-6 | [Wat is dit?](https://github.com/{os.environ.get("GITHUB_REPOSITORY", "")}/blob/main/scripts/pm/triage_issue.py)</sub>
"""


# ---------------------------------------------------------------------------
# Hoofdfunctie
# ---------------------------------------------------------------------------

def triageer_issue(repo: str, issue_number: int, github_token: str, anthropic_key: str) -> None:
    """Voer volledige triage uit op een GitHub issue."""

    print(f"Triage starten voor issue #{issue_number} in {repo}...")

    # Haal issue op
    issue = haal_issue_op(repo, issue_number, github_token)
    title = issue["title"]
    body = issue.get("body") or "(geen beschrijving)"

    print(f"Issue: {title}")

    # Controleer of al getriageerd
    comments = haal_comments_op(repo, issue_number, github_token)
    if is_al_getriageerd(comments):
        print(f"Issue #{issue_number} is al getriageerd, overgeslagen.")
        return

    # Laad projectcontext
    project_context = laad_project_context()

    # Claude API aanroepen
    client = anthropic.Anthropic(api_key=anthropic_key)

    system_prompt = f"""Je bent de AI Product Manager voor de Softwarecatalogus van VNG Realisatie.
Je taak is het triageren van GitHub issues op basis van de projectdocumentatie.

Hieronder volgt de volledige projectdocumentatie (CLAUDE.md):

<projectdocumentatie>
{project_context}
</projectdocumentatie>

Analyseer het issue zorgvuldig en geef een gestructureerde triageuitkomst terug.
Gebruik ALTIJD het Nederlands in je antwoorden.
Wees concreet en praktisch in acceptatiecriteria en technische aanpak.

BELANGRIJK: Geef je antwoord UITSLUITEND als geldig JSON-object, zonder extra tekst ervoor of erna.
Het JSON-object moet exact deze velden bevatten:
{
  "prioriteit": "kritiek"|"hoog"|"gemiddeld"|"laag",
  "type": "bug"|"feature"|"enhancement"|"docs"|"infra"|"vraag",
  "componenten": ["backend"|"frontend"|"api"|"auth"|"gemma"|"zoeken"|"export"|"documenten"|"organisaties"|"pakketten"|"infra"],
  "fase": "fase-1"|"fase-2"|"fase-3"|"fase-4"|"fase-5"|null,
  "eis_of_wens": "eis"|"wens"|"intern",
  "complexiteit": "klein"|"gemiddeld"|"groot"|"epic",
  "auto_implementeerbaar": true|false,
  "samenvatting": "string",
  "acceptatiecriteria": ["string"],
  "technische_aanpak": "string",
  "rationale": "string",
  "gerelateerde_eisen": ["string"],
  "risicos": ["string"]
}"""

    user_message = f"""Triageer het volgende GitHub issue:

**Titel:** {title}

**Beschrijving:**
{body}

**Huidige labels:** {", ".join(l["name"] for l in issue.get("labels", [])) or "geen"}

Voer een volledige triage uit en geef alle velden terug."""

    print("Claude API aanroepen voor triage-analyse...")

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    # Parseer JSON uit de response tekst
    response_text = next(
        block.text for block in response.content if block.type == "text"
    )

    # Extraheer JSON-blok uit markdown code block indien aanwezig
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Probeer de volledige tekst te parsen, of zoek naar het eerste {
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        json_str = response_text[start:end] if start >= 0 else response_text

    triage_data = json.loads(json_str)
    triage = IssueTriage(**triage_data)

    print(f"Triage voltooid: {triage.prioriteit} / {triage.type} / {triage.complexiteit}")

    # Labels aanmaken en toevoegen
    labels = triage_naar_labels(triage)
    print(f"Labels toevoegen: {labels}")
    voeg_labels_toe(repo, issue_number, labels, github_token)

    # Triage-comment plaatsen
    comment = maak_triage_comment(issue, triage)
    plaats_comment(repo, issue_number, comment, github_token)

    print(f"Triage succesvol afgerond voor issue #{issue_number}!")

    # Output voor GitHub Actions
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"prioriteit={triage.prioriteit}\n")
            f.write(f"auto_implementeerbaar={str(triage.auto_implementeerbaar).lower()}\n")
            f.write(f"complexiteit={triage.complexiteit}\n")
            f.write(f"issue_type={triage.type}\n")


def main():
    parser = argparse.ArgumentParser(description="AI PM Issue Triage")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--issue", type=int, default=int(os.environ.get("ISSUE_NUMBER", "0")))
    args = parser.parse_args()

    github_token = os.environ.get("GITHUB_TOKEN")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    if not github_token:
        print("FOUT: GITHUB_TOKEN omgevingsvariabele niet ingesteld", file=sys.stderr)
        sys.exit(1)
    if not anthropic_key:
        print("FOUT: ANTHROPIC_API_KEY omgevingsvariabele niet ingesteld", file=sys.stderr)
        sys.exit(1)
    if not args.repo:
        print("FOUT: --repo of GITHUB_REPOSITORY niet ingesteld", file=sys.stderr)
        sys.exit(1)
    if not args.issue:
        print("FOUT: --issue of ISSUE_NUMBER niet ingesteld", file=sys.stderr)
        sys.exit(1)

    triageer_issue(args.repo, args.issue, github_token, anthropic_key)


if __name__ == "__main__":
    main()
