#!/usr/bin/env python3
"""
AI PM — Issue Automatische Implementatie
=========================================
Vraagt Claude om een GitHub issue te analyseren en een implementatieplan
te genereren. Past vervolgens de gesuggereerde wijzigingen toe via de
Anthropic Messages API met tool use (file lezen/schrijven).

Dit script draait vanuit de repository root in een GitHub Actions runner.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import anthropic

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CLAUDE_MODEL = "claude-opus-4-6"
MAX_TOKENS = 8192

TOOLS = [
    {
        "name": "read_file",
        "description": "Lees de inhoud van een bestand in de repository.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relatief pad vanaf de repository root"}
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Schrijf of overschrijf een bestand in de repository.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relatief pad vanaf de repository root"},
                "content": {"type": "string", "description": "Volledige nieuwe inhoud van het bestand"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "run_command",
        "description": "Voer een shell-commando uit in de repository root (bijv. pytest, npm test).",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Het uit te voeren commando"},
            },
            "required": ["command"],
        },
    },
    {
        "name": "list_files",
        "description": "Lijst bestanden op in een map (niet-recursief).",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relatief pad naar de map"},
            },
            "required": ["path"],
        },
    },
]


def handle_tool(name: str, inputs: dict) -> str:
    try:
        if name == "read_file":
            p = REPO_ROOT / inputs["path"]
            if not p.exists():
                return f"FOUT: bestand niet gevonden: {inputs['path']}"
            return p.read_text(encoding="utf-8", errors="replace")[:8000]

        if name == "write_file":
            p = REPO_ROOT / inputs["path"]
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(inputs["content"], encoding="utf-8")
            return f"Geschreven: {inputs['path']} ({len(inputs['content'])} bytes)"

        if name == "run_command":
            result = subprocess.run(
                inputs["command"],
                shell=True,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=120,
            )
            output = (result.stdout + result.stderr)[:4000]
            return f"Exit {result.returncode}:\n{output}"

        if name == "list_files":
            p = REPO_ROOT / inputs["path"]
            if not p.exists():
                return f"FOUT: map niet gevonden: {inputs['path']}"
            entries = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name))
            return "\n".join(
                f"{'[dir] ' if e.is_dir() else '      '}{e.name}" for e in entries[:50]
            )

    except Exception as e:
        return f"FOUT bij {name}: {e}"

    return f"Onbekende tool: {name}"


def git_commit(issue_num: str, title: str) -> None:
    subprocess.run(["git", "add", "-A"], cwd=REPO_ROOT, check=False)
    msg = f"feat: implementatie issue #{issue_num} — {title[:60]}\n\nCloses #{issue_num}"
    result = subprocess.run(
        ["git", "commit", "-m", msg],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"Git commit aangemaakt: {msg[:80]}")
    else:
        print(f"Git commit mislukt of niets te committen: {result.stderr[:200]}")


def main() -> int:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("FOUT: ANTHROPIC_API_KEY niet ingesteld", file=sys.stderr)
        return 1

    issue_num = os.environ.get("ISSUE_NUM", "0")
    issue_title = os.environ.get("ISSUE_TITLE", "Onbekend issue")
    issue_data_raw = os.environ.get("ISSUE_DATA", "{}")

    try:
        issue_data = json.loads(issue_data_raw)
    except json.JSONDecodeError:
        issue_data = {"raw": issue_data_raw}

    # Lees CLAUDE.md voor projectcontext
    claude_md_path = REPO_ROOT / "CLAUDE.md"
    claude_md = claude_md_path.read_text(encoding="utf-8")[:3000] if claude_md_path.exists() else ""

    system_prompt = f"""Je bent een senior fullstack developer voor de Softwarecatalogus (VNG Realisatie).
Je taak is om een GitHub issue volledig en correct te implementeren in de bestaande codebase.

Projectcontext (CLAUDE.md samenvatting):
{claude_md}

Werkwijze:
1. Lees eerst de relevante bestanden om de codebase te begrijpen.
2. Implementeer de gevraagde wijziging(en) — niet meer, niet minder.
3. Schrijf tests als dat van toepassing is.
4. Verifieer dat de wijzigingen correct zijn (optioneel: draai tests).
5. Geef een korte samenvatting van wat je hebt gedaan.

Regels:
- Gebruik ALLEEN de aangeleverde tools (read_file, write_file, run_command, list_files).
- Schrijf in het Nederlands (variabelen/code in het Engels).
- Commit NIET zelf — dat doet de workflow na afloop.
- Wees precies en voorzichtig. Verander geen code die niet gevraagd wordt."""

    user_prompt = f"""Implementeer het volgende GitHub issue:

**Issue #{issue_num}: {issue_title}**

Issue details:
```json
{json.dumps(issue_data, ensure_ascii=False, indent=2)[:3000]}
```

Begin met het lezen van relevante bestanden, implementeer daarna de wijzigingen."""

    client = anthropic.Anthropic(api_key=api_key)
    messages = [{"role": "user", "content": user_prompt}]

    print(f"Implementatie gestart voor issue #{issue_num}: {issue_title}")
    turns = 0
    max_turns = 20

    while turns < max_turns:
        turns += 1
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        # Verwerk tool-aanroepen
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  Tool: {block.name}({list(block.input.keys())})")
                result = handle_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        # Voeg assistant-response toe aan messages
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Implementatie voltooid
            for block in response.content:
                if hasattr(block, "text"):
                    print("Samenvatting:", block.text[:400])
            break

        if tool_results:
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    # Commit de wijzigingen
    git_commit(issue_num, issue_title)
    print(f"Implementatie voltooid na {turns} iteraties.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
