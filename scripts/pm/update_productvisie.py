#!/usr/bin/env python3
"""
AI Product Manager — Productvisie & Roadmap Updater
====================================================
Analyseert de actuele projectstatus (issues, milestones, closed/open items)
en werkt docs/product/PRODUCTVISIE-ROADMAP.md automatisch bij.

Werking:
  1. Haalt alle GitHub issues op (open + gesloten)
  2. Leest het huidige PRODUCTVISIE-ROADMAP.md
  3. Vraagt Claude om een bijgewerkte versie te genereren
  4. Commit + push naar main via de GitHub Contents API
  5. Plaatst een samenvattend comment op het tracking-issue (#53)

Gebruik (lokaal):
  ANTHROPIC_API_KEY=... GITHUB_TOKEN=... python update_productvisie.py

Via GitHub Actions:
  Zie .github/workflows/pm-productvisie.yml
"""

import base64
import json
import os
import sys
from datetime import date
from pathlib import Path

import anthropic
import requests
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Configuratie
# ---------------------------------------------------------------------------

REPO = os.environ.get("GITHUB_REPOSITORY", "surfdude1978/softwarecatalogus")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
DOC_PATH = "docs/product/PRODUCTVISIE-ROADMAP.md"
TRACKING_ISSUE = 53  # Issue dat als "pinned" statusupdate dient
CLAUDE_MODEL = "claude-opus-4-6"

HEADERS_GH = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# GitHub helpers
# ---------------------------------------------------------------------------

def gh_get(path: str, params: dict | None = None) -> list | dict:
    url = f"https://api.github.com/repos/{REPO}/{path}"
    results = []
    page = 1
    while True:
        r = requests.get(
            url,
            headers=HEADERS_GH,
            params={**(params or {}), "per_page": 100, "page": page},
        )
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list):
            results.extend(data)
            if len(data) < 100:
                break
            page += 1
        else:
            return data
    return results


def get_file_sha(path: str) -> str | None:
    """Haal de huidige SHA op van een bestand in main (nodig voor update)."""
    try:
        r = requests.get(
            f"https://api.github.com/repos/{REPO}/contents/{path}",
            headers=HEADERS_GH,
            params={"ref": "main"},
        )
        if r.status_code == 200:
            return r.json()["sha"]
    except Exception:
        pass
    return None


def push_file(path: str, content: str, commit_message: str, sha: str | None) -> str:
    """Maak of update een bestand op main via de Contents API."""
    payload: dict = {
        "message": commit_message,
        "content": base64.b64encode(content.encode()).decode(),
        "branch": "main",
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(
        f"https://api.github.com/repos/{REPO}/contents/{path}",
        headers=HEADERS_GH,
        json=payload,
    )
    r.raise_for_status()
    return r.json()["commit"]["sha"]


def post_issue_comment(issue_number: int, body: str) -> None:
    requests.post(
        f"https://api.github.com/repos/{REPO}/issues/{issue_number}/comments",
        headers=HEADERS_GH,
        json={"body": body},
    )


# ---------------------------------------------------------------------------
# Data verzamelen
# ---------------------------------------------------------------------------

def collect_project_snapshot() -> dict:
    """Verzamel alle relevante projectdata voor de AI-PM analyse."""
    print("Ophalen issues...")
    all_issues = gh_get("issues", {"state": "all"})

    open_issues = [i for i in all_issues if i["state"] == "open" and not i.get("pull_request")]
    closed_issues = [i for i in all_issues if i["state"] == "closed" and not i.get("pull_request")]

    def summarize_issue(i: dict) -> dict:
        return {
            "number": i["number"],
            "title": i["title"],
            "state": i["state"],
            "labels": [l["name"] for l in i.get("labels", [])],
            "created_at": i["created_at"][:10],
            "closed_at": (i.get("closed_at") or "")[:10] or None,
        }

    # Label-statistieken
    label_counts: dict[str, int] = {}
    for issue in all_issues:
        for label in issue.get("labels", []):
            label_counts[label["name"]] = label_counts.get(label["name"], 0) + 1

    # Recent gesloten (laatste 30 dagen)
    from datetime import datetime, timedelta
    cutoff = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    recent_closed = [
        summarize_issue(i) for i in closed_issues
        if (i.get("closed_at") or "") >= cutoff
    ]

    print(f"  Open: {len(open_issues)}, Gesloten: {len(closed_issues)}, Recent gesloten: {len(recent_closed)}")

    return {
        "datum": str(date.today()),
        "totaal_issues": len(all_issues),
        "open_issues": len(open_issues),
        "gesloten_issues": len(closed_issues),
        "label_statistieken": dict(sorted(label_counts.items(), key=lambda x: -x[1])[:20]),
        "open_issues_detail": [summarize_issue(i) for i in open_issues],
        "recent_gesloten": recent_closed,
        "alle_gesloten_labels": list({
            l for i in closed_issues for l in [lb["name"] for lb in i.get("labels", [])]
        }),
    }


def load_current_doc() -> str:
    """Lees het huidige PRODUCTVISIE-ROADMAP.md vanuit de repo of lokaal."""
    local = BASE_DIR / DOC_PATH
    if local.exists():
        return local.read_text(encoding="utf-8")
    # Fallback: haal op via GitHub API
    r = requests.get(
        f"https://api.github.com/repos/{REPO}/contents/{DOC_PATH}",
        headers=HEADERS_GH,
        params={"ref": "main"},
    )
    if r.status_code == 200:
        return base64.b64decode(r.json()["content"]).decode("utf-8")
    return ""


def load_claude_md() -> str:
    claude_md = BASE_DIR / "CLAUDE.md"
    if claude_md.exists():
        # Geef alleen de eerste ~3000 tekens mee (context-beperking)
        content = claude_md.read_text(encoding="utf-8")
        return content[:3000] + "\n...[ingekort]" if len(content) > 3000 else content
    return ""


# ---------------------------------------------------------------------------
# AI-PM aanroepen
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """Je bent een ervaren Product Manager voor de Softwarecatalogus van VNG Realisatie.
Je taak is om het bestaande productvisie- en roadmap-document bij te werken op basis van de actuele projectstatus.

Regels:
- Behoud de volledige structuur en alle 11 hoofdstukken van het bestaande document.
- Werk uitsluitend factfeitelijke secties bij op basis van de aangeleverde data:
  * Sectie 2.1: kernfunctionaliteiten tabelstatus (✅/🔲/⚠️)
  * Sectie 3 (Roadmap): issue-nummers, fase-indeling, open/gesloten status
  * Sectie 6 (Gap-analyse): huidige productstatus tabel, knelpunten, quick wins
  * Sectie 7 (Volwassenheid): scores aanpassen op basis van voortgang
  * Sectie 12 bijlage: issue-overzicht bijwerken
- Pas de datumregel bovenaan het document aan naar de huidige datum.
- Voeg een changelog-regel toe onder de datumregel: "**Laatste update:** [datum] — automatische statusupdate"
- Schrijf in het Nederlands.
- Geef ALLEEN het volledige bijgewerkte markdown-document terug, zonder preamble of uitleg.
- Behoud de EUPL-1.2 licentie-verwijzingen en alle strategische adviesteksten ongewijzigd.
"""


def update_document_with_claude(snapshot: dict, current_doc: str, claude_md_context: str) -> str:
    print("Claude aanroepen voor documentupdate...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    user_message = f"""Actuele projectsnapshot ({snapshot['datum']}):

```json
{json.dumps(snapshot, ensure_ascii=False, indent=2)}
```

Projectcontext (CLAUDE.md samenvatting):
{claude_md_context}

Huidig document om bij te werken:
{current_doc}

Geef het volledig bijgewerkte document terug."""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    updated = message.content[0].text.strip()
    # Verwijder eventuele markdown code-fence wrapper
    if updated.startswith("```markdown"):
        updated = updated[len("```markdown"):].strip()
    if updated.startswith("```"):
        updated = updated[3:].strip()
    if updated.endswith("```"):
        updated = updated[:-3].strip()

    return updated


# ---------------------------------------------------------------------------
# Samenvatting voor tracking issue
# ---------------------------------------------------------------------------

def build_comment(snapshot: dict) -> str:
    open_p1 = [
        f"#{i['number']} {i['title'][:60]}"
        for i in snapshot["open_issues_detail"]
        if any(l in ("priority:critical", "priority:high", "security") for l in i["labels"])
    ]
    recent = [f"#{i['number']} {i['title'][:60]}" for i in snapshot["recent_gesloten"][:5]]

    open_list = "\n".join(f"- {x}" for x in open_p1) or "- Geen open P1/P2 issues"
    recent_list = "\n".join(f"- {x}" for x in recent) or "- Geen recente sluitingen"

    return f"""### Automatische statusupdate — {snapshot['datum']}

**Backlog:** {snapshot['open_issues']} open / {snapshot['gesloten_issues']} gesloten / {snapshot['totaal_issues']} totaal

**Open hoge prioriteit / security:**
{open_list}

**Recent gesloten (30 dagen):**
{recent_list}

[Volledig bijgewerkt document](https://github.com/{REPO}/blob/main/{DOC_PATH})

---
*Automatisch gegenereerd door AI PM workflow*"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    if not GITHUB_TOKEN:
        print("FOUT: GITHUB_TOKEN niet ingesteld", file=sys.stderr)
        return 1
    if not ANTHROPIC_API_KEY:
        print("FOUT: ANTHROPIC_API_KEY niet ingesteld", file=sys.stderr)
        return 1

    # 1. Data verzamelen
    snapshot = collect_project_snapshot()

    # 2. Huidig document laden
    print("Huidig document laden...")
    current_doc = load_current_doc()
    if not current_doc:
        print("FOUT: Huidig document niet gevonden", file=sys.stderr)
        return 1
    claude_md = load_claude_md()

    # 3. Claude updatet het document
    updated_doc = update_document_with_claude(snapshot, current_doc, claude_md)

    # 4. Controleer of er iets veranderd is
    if updated_doc.strip() == current_doc.strip():
        print("Geen wijzigingen — document is al actueel.")
        return 0

    # 5. Push naar main
    print("Document pushen naar main...")
    sha = get_file_sha(DOC_PATH)
    commit_sha = push_file(
        DOC_PATH,
        updated_doc,
        f"docs(product): automatische statusupdate productvisie ({snapshot['datum']})",
        sha,
    )
    print(f"Gepusht: {commit_sha[:12]}")

    # 6. Lokaal bestand bijwerken (voor CI-context)
    local_path = BASE_DIR / DOC_PATH
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(updated_doc, encoding="utf-8")

    # 7. Samenvatting op tracking issue
    print(f"Comment plaatsen op issue #{TRACKING_ISSUE}...")
    post_issue_comment(TRACKING_ISSUE, build_comment(snapshot))

    print("Klaar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
