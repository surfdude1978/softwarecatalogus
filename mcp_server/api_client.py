# SPDX-License-Identifier: EUPL-1.2
"""HTTP-client voor de Softwarecatalogus REST API."""

from __future__ import annotations

import httpx

from .config import API_BASE_URL, AUTH_TOKEN


class SoftwarecatalogusClient:
    """Async HTTP-client die de Softwarecatalogus API aanroept."""

    def __init__(
        self,
        base_url: str = API_BASE_URL,
        auth_token: str | None = AUTH_TOKEN,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy-initialiseer de httpx AsyncClient."""
        if self._client is None or self._client.is_closed:
            headers: dict[str, str] = {"Accept": "application/json"}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=30.0,
            )
        return self._client

    @staticmethod
    def _clean_params(params: dict | None) -> dict:
        """Verwijder None-waarden uit query-parameters."""
        if not params:
            return {}
        return {k: v for k, v in params.items() if v is not None}

    async def get(self, path: str, params: dict | None = None) -> dict | list:
        """Voer een GET-request uit naar de API.

        Raises:
            RuntimeError: Als de API niet bereikbaar is of een fout teruggeeft.
        """
        client = await self._get_client()
        try:
            response = await client.get(path, params=self._clean_params(params))
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            raise RuntimeError(
                f"De Softwarecatalogus API is niet bereikbaar op {self.base_url}. "
                "Controleer of de backend draait (docker compose up backend)."
            )
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"API-fout {exc.response.status_code}: {exc.response.text[:200]}"
            )

    async def close(self) -> None:
        """Sluit de HTTP-client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Singleton client-instantie
client = SoftwarecatalogusClient()
