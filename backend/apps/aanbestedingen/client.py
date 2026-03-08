"""
TenderNed Open Data API client.

Synchroniseert ICT-aanbestedingen van Nederlandse gemeenten vanuit TenderNed.
Gebruikt de TenderNed Open Data REST API (JSON).

API documentatie: https://www.tenderned.nl/cms/nl/aankondigingen-opendata
Endpoint: https://www.tenderned.nl/aankondigingen/api/aankondigingen
"""
import logging
from datetime import date, timedelta
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# CPV-codes voor ICT-gerelateerde aanbestedingen
ICT_CPV_CODES = [
    "48000000",  # Software en aanverwante pakketten
    "48100000",  # Sectorgebonden softwarepakket
    "48200000",  # Pakket voor netwerk-, internet- en intranetgerelateerde software
    "48300000",  # Document creation, drawing, imaging, scheduling and productivity software package
    "48400000",  # Zakelijk transactie- en persoonlijk programmatuur
    "48500000",  # Communications software package
    "48600000",  # Database- en besturingssoftware
    "48700000",  # Software utility packages
    "48800000",  # Informatiesystemen en servers
    "48900000",  # Miscellaneous software packages and computer systems
    "72000000",  # IT-diensten: advies, softwareontwikkeling, internet en ondersteuning
    "72100000",  # Advies inzake hardware
    "72200000",  # Programmering van en advies inzake software
    "72210000",  # Programming services of packaged software products
    "72220000",  # Systems and technical consultancy services
    "72230000",  # Custom software development services
    "72240000",  # Systems analysis and programming services
    "72250000",  # System and support services
    "72260000",  # Diensten in verband met software
    "72300000",  # Gegevensdiensten
    "72310000",  # Data processing services
    "72314000",  # Data collection and collation services
    "72315000",  # Data network management and support services
    "72316000",  # Data analysis services
    "72317000",  # Data storage services
    "72318000",  # Data transmission services
    "72319000",  # Data supply services
    "72400000",  # Internetdiensten
    "72500000",  # Computergerelateerde diensten
    "72600000",  # Computer ondersteunings- en consultancydiensten
    "72700000",  # Computernets en diensten daarvoor
    "72800000",  # Audits in verband met computers en testdiensten
    "72900000",  # Computer back-up and catalogue conversion services
]

# CPV-code prefix → GEMMA componentnaam mapping
CPV_GEMMA_MAPPING = {
    "48100": "Zaaksysteem",
    "48200": "Netwerk en infrastructuur",
    "48400": "Financieel systeem",
    "48600": "Gegevensbeheer",
    "48800": "ICT-infrastructuur",
    "72200": "Maatwerksoftware ontwikkeling",
    "72300": "Datadiensten",
    "72500": "ICT-beheer",
    "72600": "ICT-ondersteuning",
    "72700": "Netwerk en infrastructuur",
    "48000": "Software pakket",
    "72000": "IT-diensten",
}


# ---------------------------------------------------------------------------
# Realistische demo-data met echte Nederlandse gemeente aanbestedingen
# ---------------------------------------------------------------------------
DEMO_AANBESTEDINGEN = [
    {
        "publicatiecode": "2024-567891",
        "naam": "Zaaksysteem voor burgerzakendienstverlening gemeente Amsterdam",
        "aanbestedende_dienst": "Gemeente Amsterdam",
        "aanbestedende_dienst_stad": "Amsterdam",
        "type": "europees",
        "status": "aankondiging",
        "procedure": "Openbare procedure",
        "publicatiedatum": (date.today() - timedelta(days=3)).isoformat(),
        "sluitingsdatum": (date.today() + timedelta(days=25)).isoformat(),
        "cpv_codes": ["72230000", "48100000"],
        "cpv_omschrijvingen": [
            "Custom software development services",
            "Sectorgebonden softwarepakket",
        ],
        "waarde_geschat": 2500000.00,
        "url_tenderned": "https://www.tenderned.nl/aankondigingen/overzicht/2024-567891",
        "omschrijving": (
            "Gemeente Amsterdam zoekt een moderne zaaksysteem-oplossing voor de "
            "afhandeling van burgerzaken. Het systeem dient te integreren met "
            "DigiD, mijn.overheid.nl en de bestaande backoffice-systemen."
        ),
    },
    {
        "publicatiecode": "2024-568445",
        "naam": "Levering en implementatie financieel managementsysteem",
        "aanbestedende_dienst": "Gemeente Utrecht",
        "aanbestedende_dienst_stad": "Utrecht",
        "type": "europees",
        "status": "aankondiging",
        "procedure": "Niet-openbare procedure",
        "publicatiedatum": (date.today() - timedelta(days=5)).isoformat(),
        "sluitingsdatum": (date.today() + timedelta(days=30)).isoformat(),
        "cpv_codes": ["48400000", "72260000"],
        "cpv_omschrijvingen": [
            "Zakelijk transactie- en persoonlijk programmatuur",
            "Diensten in verband met software",
        ],
        "waarde_geschat": 1800000.00,
        "url_tenderned": "https://www.tenderned.nl/aankondigingen/overzicht/2024-568445",
        "omschrijving": (
            "Gemeente Utrecht vraagt financieel managementsysteem inclusief "
            "inkoop, crediteuren, debiteuren, grootboek en rapportage. "
            "Koppeling met P-Direktportaal en Rijksconnect vereist."
        ),
    },
    {
        "publicatiecode": "2024-569012",
        "naam": "ICT-werkplekbeheer en servicedesk dienstverlening 2025-2029",
        "aanbestedende_dienst": "Gemeente Rotterdam",
        "aanbestedende_dienst_stad": "Rotterdam",
        "type": "europees",
        "status": "aankondiging",
        "procedure": "Openbare procedure",
        "publicatiedatum": (date.today() - timedelta(days=7)).isoformat(),
        "sluitingsdatum": (date.today() + timedelta(days=42)).isoformat(),
        "cpv_codes": ["72600000", "72500000", "72700000"],
        "cpv_omschrijvingen": [
            "Computer ondersteunings- en consultancydiensten",
            "Computergerelateerde diensten",
            "Computernets en diensten daarvoor",
        ],
        "waarde_geschat": 12000000.00,
        "url_tenderned": "https://www.tenderned.nl/aankondigingen/overzicht/2024-569012",
        "omschrijving": (
            "Raamovereenkomst voor het beheer van ca. 8.500 werkplekken en "
            "centrale servicedesk. Inclusief hardware lifecycle management, "
            "Microsoft 365 beheer en security monitoring."
        ),
    },
    {
        "publicatiecode": "2024-570334",
        "naam": "Software voor vergunningverlening, toezicht en handhaving (VTH)",
        "aanbestedende_dienst": "Gemeente Den Haag",
        "aanbestedende_dienst_stad": "Den Haag",
        "type": "europees",
        "status": "aankondiging",
        "procedure": "Openbare procedure",
        "publicatiedatum": (date.today() - timedelta(days=10)).isoformat(),
        "sluitingsdatum": (date.today() + timedelta(days=21)).isoformat(),
        "cpv_codes": ["48100000", "72230000", "72260000"],
        "cpv_omschrijvingen": [
            "Sectorgebonden softwarepakket",
            "Custom software development services",
            "Diensten in verband met software",
        ],
        "waarde_geschat": 950000.00,
        "url_tenderned": "https://www.tenderned.nl/aankondigingen/overzicht/2024-570334",
        "omschrijving": (
            "Omgevingsdienst Haaglanden en Gemeente Den Haag zoeken een "
            "geïntegreerde VTH-applicatie. Vereist koppeling met DSO "
            "(Digitaal Stelsel Omgevingswet) en BAG/BGT-basisregistraties."
        ),
    },
    {
        "publicatiecode": "2024-571890",
        "naam": "Documentmanagementsysteem (DMS) en archivering",
        "aanbestedende_dienst": "Gemeente Eindhoven",
        "aanbestedende_dienst_stad": "Eindhoven",
        "type": "nationaal",
        "status": "aankondiging",
        "procedure": "Meervoudig onderhands",
        "publicatiedatum": (date.today() - timedelta(days=12)).isoformat(),
        "sluitingsdatum": (date.today() + timedelta(days=14)).isoformat(),
        "cpv_codes": ["48600000", "72300000"],
        "cpv_omschrijvingen": [
            "Database- en besturingssoftware",
            "Gegevensdiensten",
        ],
        "waarde_geschat": 350000.00,
        "url_tenderned": "https://www.tenderned.nl/aankondigingen/overzicht/2024-571890",
        "omschrijving": (
            "DMS voor digitale archivering conform NEN 2082 en e-Depot "
            "aansluiting. Moet integreren met het bestaande zaaksysteem "
            "en voldoen aan de Archiefwet 2021."
        ),
    },
    {
        "publicatiecode": "2024-572567",
        "naam": "HR-systeem en salarisverwerking gemeente Breda",
        "aanbestedende_dienst": "Gemeente Breda",
        "aanbestedende_dienst_stad": "Breda",
        "type": "europees",
        "status": "gunning",
        "procedure": "Openbare procedure",
        "publicatiedatum": (date.today() - timedelta(days=20)).isoformat(),
        "sluitingsdatum": None,
        "cpv_codes": ["48400000", "48000000"],
        "cpv_omschrijvingen": [
            "Zakelijk transactie- en persoonlijk programmatuur",
            "Software en aanverwante pakketten",
        ],
        "waarde_geschat": 780000.00,
        "url_tenderned": "https://www.tenderned.nl/aankondigingen/overzicht/2024-572567",
        "omschrijving": (
            "Gegunde opdracht voor nieuw HR- en salarissysteem. "
            "Opdracht gegund aan Centric voor implementatie van "
            "PinkRoccade HR en PayRoll suite."
        ),
    },
    {
        "publicatiecode": "2024-573201",
        "naam": "Cloud-migratie en modernisering ICT-infrastructuur",
        "aanbestedende_dienst": "Gemeenschappelijke Regeling ICT West-Brabant",
        "aanbestedende_dienst_stad": "Tilburg",
        "type": "europees",
        "status": "aankondiging",
        "procedure": "Openbare procedure",
        "publicatiedatum": (date.today() - timedelta(days=14)).isoformat(),
        "sluitingsdatum": (date.today() + timedelta(days=35)).isoformat(),
        "cpv_codes": ["72800000", "72500000", "48800000"],
        "cpv_omschrijvingen": [
            "Audits in verband met computers en testdiensten",
            "Computergerelateerde diensten",
            "Informatiesystemen en servers",
        ],
        "waarde_geschat": 5500000.00,
        "url_tenderned": "https://www.tenderned.nl/aankondigingen/overzicht/2024-573201",
        "omschrijving": (
            "Raamovereenkomst voor cloud-migratie van on-premise systemen "
            "naar Azure Government. Betreft 12 gemeenten en 2 "
            "samenwerkingsverbanden in West-Brabant."
        ),
    },
    {
        "publicatiecode": "2024-574100",
        "naam": "Burgerpanel en e-participatie platform",
        "aanbestedende_dienst": "Gemeente Nijmegen",
        "aanbestedende_dienst_stad": "Nijmegen",
        "type": "nationaal",
        "status": "aankondiging",
        "procedure": "Openbare aanbesteding",
        "publicatiedatum": (date.today() - timedelta(days=2)).isoformat(),
        "sluitingsdatum": (date.today() + timedelta(days=28)).isoformat(),
        "cpv_codes": ["72200000", "48000000"],
        "cpv_omschrijvingen": [
            "Programmering van en advies inzake software",
            "Software en aanverwante pakketten",
        ],
        "waarde_geschat": 220000.00,
        "url_tenderned": "https://www.tenderned.nl/aankondigingen/overzicht/2024-574100",
        "omschrijving": (
            "SaaS-platform voor digitale burgerparticipatie, enquêtes en "
            "co-creatietrajecten. AVG-compliant, hosting in Nederland."
        ),
    },
]


class TenderNedClient:
    """
    Client voor de TenderNed Open Data API.

    Ondersteunt zowel live API-calls als demo-modus met voorbeelddata.
    In demo-modus worden de DEMO_AANBESTEDINGEN teruggegeven zodat
    de integratie werkt zonder netwerktoegang.
    """

    BASE_URL = "https://www.tenderned.nl/aankondigingen/api/aankondigingen"

    def __init__(self, demo_mode: bool = False, base_url: Optional[str] = None):
        self.demo_mode = demo_mode or getattr(settings, "TENDERNED_DEMO_MODE", True)
        self.base_url = base_url or getattr(settings, "TENDERNED_API_URL", self.BASE_URL)
        self.timeout = getattr(settings, "TENDERNED_TIMEOUT", 30)

    def haal_ict_aanbestedingen_op(
        self,
        dagen_terug: int = 30,
        max_resultaten: int = 100,
    ) -> list[dict]:
        """
        Haal ICT-aanbestedingen op van TenderNed.

        Args:
            dagen_terug: Hoeveel dagen terug te zoeken
            max_resultaten: Maximum aantal resultaten

        Returns:
            Lijst van aanbesteding-dicts
        """
        if self.demo_mode:
            logger.info("TenderNed demo-modus: voorbeelddata teruggeven")
            return DEMO_AANBESTEDINGEN[:max_resultaten]

        return self._haal_van_api(dagen_terug, max_resultaten)

    def _haal_van_api(self, dagen_terug: int, max_resultaten: int) -> list[dict]:
        """Haal aanbestedingen op van de echte TenderNed API."""
        resultaten = []
        pagina = 0
        pagina_grootte = 25

        vanaf_datum = (date.today() - timedelta(days=dagen_terug)).isoformat()

        while len(resultaten) < max_resultaten:
            try:
                response = requests.get(
                    self.base_url,
                    params={
                        "pageNumber": pagina,
                        "resultaatPerPagina": pagina_grootte,
                        "publicatieDatumVanaf": vanaf_datum,
                    },
                    timeout=self.timeout,
                    headers={
                        "Accept": "application/json",
                        "User-Agent": "Softwarecatalogus-VNG/1.0",
                    },
                )
                response.raise_for_status()
                data = response.json()

            except requests.RequestException as exc:
                logger.warning("TenderNed API fout op pagina %d: %s", pagina, exc)
                break

            aankondigingen = data.get("content") or data.get("aankondigingen") or []
            if not aankondigingen:
                break

            # Filter op ICT CPV-codes
            for item in aankondigingen:
                cpv_codes = self._extraheer_cpv_codes(item)
                if self._is_ict_aanbesteding(cpv_codes):
                    resultaten.append(self._normaliseer(item, cpv_codes))

            # Stoppen bij laatste pagina
            totaal = data.get("totalElements") or data.get("totaalAantal") or 0
            if (pagina + 1) * pagina_grootte >= totaal:
                break
            pagina += 1

        logger.info("TenderNed: %d ICT-aanbestedingen opgehaald", len(resultaten))
        return resultaten[:max_resultaten]

    def _extraheer_cpv_codes(self, item: dict) -> list[str]:
        """Extraheer CPV-codes uit een TenderNed aankondiging."""
        codes = []

        # Meerdere mogelijke JSON-structuren afhankelijk van API-versie
        for veld in ("cpvCodes", "cpv_codes", "cpv", "classifications"):
            waarde = item.get(veld)
            if isinstance(waarde, list):
                for elem in waarde:
                    if isinstance(elem, str):
                        codes.append(elem[:8])  # Eerste 8 cijfers (zonder suffix)
                    elif isinstance(elem, dict):
                        code = elem.get("code") or elem.get("cpvCode") or elem.get("id", "")
                        if code:
                            codes.append(str(code)[:8])

        return list(set(codes))

    def _is_ict_aanbesteding(self, cpv_codes: list[str]) -> bool:
        """Controleer of een aanbesteding ICT-gerelateerd is."""
        ict_prefixen = tuple(
            code[:2] for code in ["48000000", "72000000"]
        )
        return any(
            code.startswith(prefix)
            for code in cpv_codes
            for prefix in ict_prefixen
        )

    def _normaliseer(self, item: dict, cpv_codes: list[str]) -> dict:
        """Normaliseer een TenderNed item naar ons datamodel."""
        # CPV-omschrijvingen samenvoegen
        omschrijvingen = []
        for veld in ("cpvCodes", "cpv_codes", "classifications"):
            waarde = item.get(veld, [])
            for elem in waarde:
                if isinstance(elem, dict):
                    omschrijving = (
                        elem.get("omschrijving")
                        or elem.get("description")
                        or elem.get("naam")
                        or ""
                    )
                    if omschrijving:
                        omschrijvingen.append(omschrijving)

        publicatiecode = (
            item.get("publicatiecode")
            or item.get("id")
            or item.get("referentie")
            or ""
        )
        url = (
            item.get("url")
            or item.get("tenderNedUrl")
            or f"https://www.tenderned.nl/aankondigingen/overzicht/{publicatiecode}"
        )

        return {
            "publicatiecode": str(publicatiecode),
            "naam": item.get("naam") or item.get("title") or item.get("omschrijving", ""),
            "aanbestedende_dienst": (
                item.get("aanbestedendeDienst")
                or item.get("aanbestedende_dienst")
                or item.get("authority", {}).get("naam", "")
                if isinstance(item.get("authority"), dict)
                else item.get("authority", "")
            ),
            "aanbestedende_dienst_stad": (
                item.get("stad")
                or item.get("city")
                or item.get("authority", {}).get("stad", "")
                if isinstance(item.get("authority"), dict)
                else ""
            ),
            "type": self._map_type(item),
            "status": self._map_status(item),
            "procedure": item.get("procedure") or item.get("procedureType") or "",
            "publicatiedatum": item.get("publicatiedatum") or item.get("publicationDate") or "",
            "sluitingsdatum": item.get("sluitingsdatum") or item.get("closingDate"),
            "cpv_codes": cpv_codes,
            "cpv_omschrijvingen": omschrijvingen,
            "waarde_geschat": item.get("geschatteWaarde") or item.get("estimatedValue"),
            "url_tenderned": url,
            "omschrijving": item.get("omschrijving") or item.get("description") or "",
        }

    def _map_type(self, item: dict) -> str:
        """Map het aanbestedingstype naar onze choices."""
        type_str = str(
            item.get("type")
            or item.get("aanbestedingstype")
            or item.get("procurementType")
            or ""
        ).lower()
        if "europees" in type_str or "eu" in type_str or "above" in type_str:
            return "europees"
        if "nationaal" in type_str or "national" in type_str:
            return "nationaal"
        return "onbekend"

    def _map_status(self, item: dict) -> str:
        """Map het aankondigingstype naar onze choices."""
        status_str = str(
            item.get("typeAankondiging")
            or item.get("announcementType")
            or item.get("status")
            or ""
        ).lower()
        if "gunning" in status_str or "award" in status_str:
            return "gunning"
        if "rectificatie" in status_str or "corrigendum" in status_str:
            return "rectificatie"
        if "vooraankondiging" in status_str or "prior" in status_str:
            return "vooraankondiging"
        return "aankondiging"


def bepaal_gemma_componenten(cpv_codes: list[str]) -> list[str]:
    """
    Bepaal relevante GEMMA-componentnamen op basis van CPV-codes.

    Returns:
        Lijst van GEMMA-componentnamen
    """
    componenten = set()
    for cpv in cpv_codes:
        for prefix, component_naam in CPV_GEMMA_MAPPING.items():
            if str(cpv).startswith(prefix):
                componenten.add(component_naam)
    return list(componenten)
