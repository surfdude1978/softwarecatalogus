# MCP Server — Softwarecatalogus

MCP-server (Model Context Protocol) die de Softwarecatalogus API beschikbaar maakt als tools voor AI-assistenten zoals Claude Code en Claude Desktop.

## Beschikbare tools

| Tool | Beschrijving |
|------|-------------|
| `zoek_pakketten` | Full-text search in de softwarecatalogus |
| `lijst_pakketten` | Bladeren en filteren van pakketten |
| `pakket_detail` | Volledige details van een pakket |
| `lijst_organisaties` | Zoek gemeenten, leveranciers, samenwerkingsverbanden |
| `organisatie_detail` | Details van een organisatie |
| `lijst_gemma_componenten` | GEMMA-referentiecomponenten |
| `gemma_kaart` | Volledige GEMMA-architectuurkaart met pakketten |
| `lijst_standaarden` | Standaarden van Forum Standaardisatie |
| `zoek_aanbestedingen` | ICT-aanbestedingen zoeken |
| `aanbesteding_detail` | Details van een aanbesteding |

## Vereisten

- Python 3.12+
- De Softwarecatalogus backend moet draaien (standaard op `http://localhost:8000`)

## Installatie

```bash
cd mcp_server
pip install -r requirements.txt
```

## Gebruik

### Standalone (stdio-transport)

```bash
# Vanuit de project-root:
python -m mcp_server
```

### Met MCP Inspector (debug)

```bash
mcp dev mcp_server/server.py
```

### Docker

```bash
docker compose up mcp-server
```

## Configuratie

### Omgevingsvariabelen

| Variabele | Default | Beschrijving |
|-----------|---------|-------------|
| `SWC_API_URL` | `http://localhost:8000` | Basis-URL van de API |
| `SWC_AUTH_TOKEN` | _(leeg)_ | Optioneel JWT-token voor beveiligde endpoints |

### Claude Code

De MCP-server wordt automatisch herkend via `.mcp.json` in de project-root.
Herstart Claude Code na installatie — de tools verschijnen dan automatisch.

### Claude Desktop

Voeg toe aan `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "softwarecatalogus": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/pad/naar/softwarecatalogus",
      "env": {
        "SWC_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

## Licentie

EUPL-1.2
