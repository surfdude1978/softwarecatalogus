# SPDX-License-Identifier: EUPL-1.2
"""Configuratie voor de Softwarecatalogus MCP Server."""

import os

# Basis-URL van de Softwarecatalogus API.
# In Docker: http://backend:8000
# Lokaal:    http://localhost:8000
API_BASE_URL: str = os.environ.get("SWC_API_URL", "http://localhost:8000")

# Optioneel: JWT-token voor beveiligde endpoints.
# Zonder token zijn alleen publieke endpoints beschikbaar.
AUTH_TOKEN: str | None = os.environ.get("SWC_AUTH_TOKEN", None)
