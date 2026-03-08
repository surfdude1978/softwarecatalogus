"""Admin-only views voor functioneel beheerders."""
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.architectuur.ameff_import import import_ameff
from .permissions import IsFunctioneelBeheerder


class GemmaImportView(APIView):
    """Importeer GEMMA componenten vanuit een AMEFF bestand (admin)."""
    permission_classes = [IsFunctioneelBeheerder]
    parser_classes = [MultiPartParser]

    def post(self, request):
        uploaded = request.FILES.get("bestand")
        if not uploaded:
            return Response(
                {"detail": "Geen bestand geupload. Stuur een AMEFF XML-bestand mee als 'bestand'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dry_run = request.data.get("dry_run", "false").lower() == "true"

        try:
            content = uploaded.read()
            stats = import_ameff(content, dry_run=dry_run)
        except Exception as e:
            return Response(
                {"detail": f"Fout bij het verwerken van het AMEFF bestand: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            "dry_run": dry_run,
            "statistieken": {
                "elementen_gevonden": stats["elements_found"],
                "relaties_gevonden": stats["relationships_found"],
                "aangemaakt": stats["created"],
                "bijgewerkt": stats["updated"],
            },
            "conflicten": stats["conflicts"],
        })
