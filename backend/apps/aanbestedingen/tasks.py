"""
Celery taken voor TenderNed synchronisatie.

Taken:
- sync_tenderned: Dagelijkse synchronisatie van ICT-aanbestedingen
- koppel_organisaties: Koppel aanbestedingen aan gemeenten in de catalogus
- koppel_gemma_componenten: GEMMA-duiding op basis van CPV-codes
"""
import logging

from celery import shared_task
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="aanbestedingen.sync_tenderned", bind=True, max_retries=3)
def sync_tenderned(self, dagen_terug: int = 30, max_resultaten: int = 200):
    """
    Synchroniseer ICT-aanbestedingen vanuit TenderNed.

    Haalt aanbestedingen op van TenderNed, slaat nieuwe op en werkt
    bestaande bij. Koppelingen met organisaties en GEMMA-componenten
    worden automatisch bijgewerkt.
    """
    from apps.aanbestedingen.client import TenderNedClient
    from apps.aanbestedingen.models import Aanbesteding

    logger.info("Starten met TenderNed synchronisatie (laatste %d dagen)", dagen_terug)
    start = timezone.now()

    client = TenderNedClient()

    try:
        aanbestedingen_data = client.haal_ict_aanbestedingen_op(
            dagen_terug=dagen_terug,
            max_resultaten=max_resultaten,
        )
    except Exception as exc:
        logger.error("TenderNed API fout: %s", exc)
        raise self.retry(exc=exc, countdown=300)

    aangemaakt = 0
    bijgewerkt = 0
    fouten = 0

    with transaction.atomic():
        for item in aanbestedingen_data:
            try:
                aanbesteding, created = Aanbesteding.objects.update_or_create(
                    publicatiecode=item["publicatiecode"],
                    defaults={
                        "naam": item["naam"][:1000],
                        "aanbestedende_dienst": item["aanbestedende_dienst"][:500],
                        "aanbestedende_dienst_stad": (item.get("aanbestedende_dienst_stad") or "")[:255],
                        "type": item.get("type", "onbekend"),
                        "status": item.get("status", "aankondiging"),
                        "procedure": (item.get("procedure") or "")[:200],
                        "publicatiedatum": item["publicatiedatum"],
                        "sluitingsdatum": item.get("sluitingsdatum"),
                        "cpv_codes": item.get("cpv_codes", []),
                        "cpv_omschrijvingen": item.get("cpv_omschrijvingen", []),
                        "waarde_geschat": item.get("waarde_geschat"),
                        "url_tenderned": item.get("url_tenderned", "")[:500],
                        "omschrijving": item.get("omschrijving", ""),
                    },
                )

                if created:
                    aangemaakt += 1
                    # Koppel meteen aan organisatie en GEMMA
                    _koppel_organisatie(aanbesteding)
                    _koppel_gemma(aanbesteding)
                else:
                    bijgewerkt += 1

            except Exception as exc:
                logger.warning(
                    "Fout bij verwerken aanbesteding %s: %s",
                    item.get("publicatiecode"),
                    exc,
                )
                fouten += 1

    duur = (timezone.now() - start).total_seconds()
    logger.info(
        "TenderNed sync klaar in %.1fs — aangemaakt: %d, bijgewerkt: %d, fouten: %d",
        duur, aangemaakt, bijgewerkt, fouten,
    )

    return {
        "aangemaakt": aangemaakt,
        "bijgewerkt": bijgewerkt,
        "fouten": fouten,
        "duur_seconden": round(duur, 1),
    }


def _koppel_organisatie(aanbesteding):
    """Koppel aanbesteding aan een organisatie in de catalogus o.b.v. naam."""
    from apps.organisaties.models import Organisatie

    naam = aanbesteding.aanbestedende_dienst.lower()

    # Probeer exacte match of gedeeltelijke match op naam
    kandidaten = Organisatie.objects.filter(
        type__in=["gemeente", "samenwerkingsverband"],
        status="actief",
    )

    for org in kandidaten:
        org_naam = org.naam.lower()
        # Verwijder "gemeente " prefix voor vergelijking
        zoek_naam = naam.replace("gemeente ", "").strip()
        org_vergelijk = org_naam.replace("gemeente ", "").strip()

        if zoek_naam == org_vergelijk or org_vergelijk in zoek_naam or zoek_naam in org_vergelijk:
            aanbesteding.organisatie = org
            aanbesteding.save(update_fields=["organisatie"])
            logger.debug(
                "Aanbesteding %s gekoppeld aan %s",
                aanbesteding.publicatiecode,
                org.naam,
            )
            return

    logger.debug(
        "Geen organisatie gevonden voor: %s",
        aanbesteding.aanbestedende_dienst,
    )


def _koppel_gemma(aanbesteding):
    """Koppel aanbesteding aan GEMMA-componenten o.b.v. CPV-codes."""
    from apps.architectuur.models import GemmaComponent
    from apps.aanbestedingen.client import bepaal_gemma_componenten

    component_namen = bepaal_gemma_componenten(aanbesteding.cpv_codes)

    if not component_namen:
        return

    gevonden_componenten = GemmaComponent.objects.filter(
        naam__in=component_namen
    )

    if gevonden_componenten.exists():
        aanbesteding.gemma_componenten.set(gevonden_componenten)
        logger.debug(
            "Aanbesteding %s gekoppeld aan GEMMA: %s",
            aanbesteding.publicatiecode,
            [c.naam for c in gevonden_componenten],
        )
