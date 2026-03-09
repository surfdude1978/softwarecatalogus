"""
Help AI endpoint — beantwoordt vragen over de Softwarecatalogus met behulp van
Claude (Anthropic). Als ANTHROPIC_API_KEY niet is ingesteld, geeft het endpoint
een 503 terug zodat de frontend graceful kan terugvallen op de zoekfunctie.
"""

import os
from pathlib import Path

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

# Pad naar docs/handleiding.md (relatief aan de project-root)
_HANDLEIDING_PAD = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "handleiding.md"

_HANDLEIDING_CACHE: str | None = None


def _laad_handleiding() -> str:
    """Laad de handleiding uit het bestand (gecached in geheugen)."""
    global _HANDLEIDING_CACHE
    if _HANDLEIDING_CACHE is None:
        try:
            _HANDLEIDING_CACHE = _HANDLEIDING_PAD.read_text(encoding="utf-8")
        except FileNotFoundError:
            _HANDLEIDING_CACHE = "Geen handleiding beschikbaar."
    return _HANDLEIDING_CACHE


class HelpVraagThrottle(AnonRateThrottle):
    """Beperkt anonieme requests tot 20 per minuut per IP."""

    rate = "20/min"


class HelpVraagAuthThrottle(UserRateThrottle):
    """Beperkt geauthenticeerde requests tot 60 per minuut."""

    rate = "60/min"


class HelpVraagView(APIView):
    """
    POST /api/v1/help/vraag/

    Verwacht:
        {
            "vraag": "Hoe voeg ik een pakket toe?",
            "context": "/mijn-landschap"   // optioneel: huidige pagina
        }

    Geeft terug:
        { "antwoord": "..." }

    Geeft 503 terug als ANTHROPIC_API_KEY niet is geconfigureerd.
    """

    permission_classes = [AllowAny]
    throttle_classes = [HelpVraagThrottle, HelpVraagAuthThrottle]

    def post(self, request):
        vraag = (request.data.get("vraag") or "").strip()
        pagina_context = (request.data.get("context") or "").strip()

        if not vraag:
            return Response({"detail": "Vraag is verplicht."}, status=400)

        if len(vraag) > 500:
            return Response({"detail": "Vraag mag maximaal 500 tekens bevatten."}, status=400)

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return Response(
                {"detail": "AI-assistent niet beschikbaar (geen API-sleutel geconfigureerd)."},
                status=503,
            )

        try:
            import anthropic
        except ImportError:
            return Response(
                {"detail": "AI-pakket niet geïnstalleerd. Voeg 'anthropic' toe aan requirements.txt."},
                status=503,
            )

        handleiding = _laad_handleiding()

        systeem_prompt = f"""Je bent een behulpzame helpdesk-assistent voor de Softwarecatalogus van VNG Realisatie.

De Softwarecatalogus is een platform voor Nederlandse gemeenten, samenwerkingsverbanden en leveranciers om software-applicaties te registreren, vergelijken en raadplegen.  # noqa: E501

Beantwoord vragen bondig, concreet en in het Nederlands. Gebruik eenvoudige stap-voor-stap instructies waar van toepassing.  # noqa: E501
Verwijs naar specifieke onderdelen van de handleiding (sectienummers of titels) als dat helpt.
Als je iets niet weet op basis van de handleiding, zeg dat dan eerlijk.

HANDLEIDING:
{handleiding}"""

        context_toevoeging = (
            f"\n\n[Context: de gebruiker bevindt zich momenteel op pagina '{pagina_context}']" if pagina_context else ""
        )

        try:
            client = anthropic.Anthropic(api_key=api_key)
            bericht = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=600,
                system=systeem_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": vraag + context_toevoeging,
                    }
                ],
            )
            antwoord = bericht.content[0].text
            return Response({"antwoord": antwoord})

        except anthropic.AuthenticationError:
            return Response(
                {"detail": "Ongeldige API-sleutel voor AI-dienst."},
                status=503,
            )
        except anthropic.RateLimitError:
            return Response(
                {"detail": "AI-dienst tijdelijk bezet. Probeer het over een moment opnieuw."},
                status=429,
            )
        except Exception as exc:
            return Response(
                {"detail": f"Fout bij AI-verzoek: {exc}"},
                status=502,
            )
