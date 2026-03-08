"""Export views voor CSV, Excel en AMEFF."""
import csv
import io
from datetime import datetime

from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from apps.architectuur.ameff_export import generate_ameff
from apps.pakketten.models import Pakket, PakketGebruik


class ExportPakkettenCSV(APIView):
    """Exporteer pakketten als CSV."""
    permission_classes = [AllowAny]

    def get(self, request):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="pakketten_{datetime.now():%Y%m%d}.csv"'
        response.write("\ufeff")  # BOM voor Excel compatibiliteit

        writer = csv.writer(response, delimiter=";")
        writer.writerow([
            "Naam", "Versie", "Status", "Leverancier", "Licentievorm",
            "Website", "Beschrijving", "Aantal gemeenten",
        ])

        pakketten = Pakket.objects.filter(
            status__in=["actief", "concept"]
        ).select_related("leverancier")

        for p in pakketten:
            writer.writerow([
                p.naam,
                p.versie,
                p.get_status_display(),
                p.leverancier.naam if p.leverancier else "",
                p.get_licentievorm_display(),
                p.website_url,
                p.beschrijving[:500],
                p.pakketgebruik_set.filter(status="in_gebruik").count(),
            ])

        return response


class ExportPakkettenExcel(APIView):
    """Exporteer pakketten als Excel (.xlsx)."""
    permission_classes = [AllowAny]

    def get(self, request):
        import openpyxl
        from openpyxl.styles import Font

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Pakketten"

        # Header
        headers = [
            "Naam", "Versie", "Status", "Leverancier", "Licentievorm",
            "Website", "Beschrijving", "Aantal gemeenten",
        ]
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)

        pakketten = Pakket.objects.filter(
            status__in=["actief", "concept"]
        ).select_related("leverancier")

        for p in pakketten:
            ws.append([
                p.naam,
                p.versie,
                p.get_status_display(),
                p.leverancier.naam if p.leverancier else "",
                p.get_licentievorm_display(),
                p.website_url,
                p.beschrijving[:500],
                p.pakketgebruik_set.filter(status="in_gebruik").count(),
            ])

        # Auto-breedte kolommen
        for col in ws.columns:
            max_length = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_length + 2, 50)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="pakketten_{datetime.now():%Y%m%d}.xlsx"'
        return response


class ExportPakketOverzichtCSV(APIView):
    """Exporteer eigen pakketoverzicht als CSV."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.organisatie:
            return HttpResponse("Geen organisatie gekoppeld.", status=400)

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="pakketoverzicht_{user.organisatie.naam}_{datetime.now():%Y%m%d}.csv"'
        )
        response.write("\ufeff")

        writer = csv.writer(response, delimiter=";")
        writer.writerow(["Pakket", "Versie", "Status gebruik", "Leverancier", "Startdatum", "Notitie"])

        gebruik = PakketGebruik.objects.filter(
            organisatie=user.organisatie
        ).select_related("pakket", "pakket__leverancier")

        for pg in gebruik:
            writer.writerow([
                pg.pakket.naam,
                pg.pakket.versie,
                pg.get_status_display(),
                pg.pakket.leverancier.naam if pg.pakket.leverancier else "",
                pg.start_datum.isoformat() if pg.start_datum else "",
                pg.notitie,
            ])

        return response


class ExportPakketOverzichtAMEFF(APIView):
    """Exporteer eigen pakketoverzicht als AMEFF (ArchiMate Exchange)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.organisatie:
            return HttpResponse("Geen organisatie gekoppeld.", status=400)

        xml_content = generate_ameff(organisatie_id=user.organisatie.id)

        response = HttpResponse(xml_content, content_type="application/xml")
        response["Content-Disposition"] = (
            f'attachment; filename="pakketoverzicht_{user.organisatie.naam}_{datetime.now():%Y%m%d}.ameff"'
        )
        return response
