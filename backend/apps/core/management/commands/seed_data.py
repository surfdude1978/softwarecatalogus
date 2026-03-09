"""
Management command om de database te vullen met realistische voorbeelddata.

Bevat echte Nederlandse gemeenten, leveranciers, pakketten, GEMMA-componenten
en standaarden die representatief zijn voor het gemeentelijke ICT-landschap.

Gebruik:
    python manage.py seed_data
    python manage.py seed_data --clear  # Verwijder eerst bestaande data
"""

import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.architectuur.models import GemmaComponent, PakketGemmaComponent
from apps.content.models import Nieuwsbericht, Pagina
from apps.gebruikers.models import Notificatie, User
from apps.organisaties.models import Contactpersoon, Organisatie
from apps.pakketten.models import Koppeling, Pakket, PakketGebruik
from apps.standaarden.models import PakketStandaard, Standaard


class Command(BaseCommand):
    help = "Vul de database met realistische voorbeelddata voor de Softwarecatalogus."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Verwijder alle bestaande data voordat de seed wordt uitgevoerd.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Bestaande data verwijderen...")
            self._clear_data()

        with transaction.atomic():
            self.stdout.write("Stap 1/9: Organisaties aanmaken...")
            gemeenten, leveranciers, swv = self._create_organisaties()

            self.stdout.write("Stap 2/9: GEMMA-componenten aanmaken...")
            componenten = self._create_gemma_componenten()

            self.stdout.write("Stap 3/9: Standaarden aanmaken...")
            standaarden = self._create_standaarden()

            self.stdout.write("Stap 4/9: Gebruikers aanmaken...")
            users = self._create_users(gemeenten, leveranciers)

            self.stdout.write("Stap 5/9: Pakketten aanmaken...")
            pakketten = self._create_pakketten(leveranciers, users)

            self.stdout.write("Stap 6/9: Pakket-standaarden koppelen...")
            self._create_pakket_standaarden(pakketten, standaarden)

            self.stdout.write("Stap 7/9: Pakket-GEMMA koppelingen aanmaken...")
            self._create_pakket_gemma(pakketten, componenten)

            self.stdout.write("Stap 8/9: Pakketgebruik en koppelingen aanmaken...")
            self._create_pakketgebruik(pakketten, gemeenten, swv)

            self.stdout.write("Stap 9/9: Content en notificaties aanmaken...")
            self._create_content(users)

            self.stdout.write("Stap 10/10: TenderNed aanbestedingen laden...")
            self._create_aanbestedingen(gemeenten)

        self.stdout.write(self.style.SUCCESS("\nSeed data succesvol aangemaakt!"))
        self._print_summary()

    def _clear_data(self):
        models = [
            Notificatie, Koppeling, PakketGebruik, PakketStandaard,
            PakketGemmaComponent, Pakket, Standaard, GemmaComponent,
            Contactpersoon, Nieuwsbericht, Pagina,
        ]
        for model in models:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f"  {model.__name__}: {count} verwijderd")
        # Users behalve superusers
        count = User.objects.filter(is_superuser=False).count()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(f"  User (niet-superusers): {count} verwijderd")
        # Organisaties als laatste (vanwege FK's)
        count = Organisatie.objects.count()
        Organisatie.objects.all().delete()
        self.stdout.write(f"  Organisatie: {count} verwijderd")

    # ──────────────────────────────────────────────────────────────
    # Organisaties
    # ──────────────────────────────────────────────────────────────

    def _create_organisaties(self):
        gemeente_data = [
            ("Gemeente Utrecht", "00000001821029457000", "0344"),
            ("Gemeente Amsterdam", "00000001002220647000", "0363"),
            ("Gemeente Rotterdam", "00000001001337625000", "0599"),
            ("Gemeente Den Haag", "00000001001478620000", "0518"),
            ("Gemeente Eindhoven", "00000001001903694000", "0772"),
            ("Gemeente Groningen", "00000001001700887000", "0014"),
            ("Gemeente Tilburg", "00000001001967947000", "0855"),
            ("Gemeente Almere", "00000001001979485000", "0034"),
            ("Gemeente Breda", "00000001001951676000", "0758"),
            ("Gemeente Nijmegen", "00000001001651976000", "0268"),
            ("Gemeente Apeldoorn", "00000001001763888000", "0200"),
            ("Gemeente Haarlem", "00000001001692680000", "0392"),
            ("Gemeente Arnhem", "00000001001605920000", "0202"),
            ("Gemeente Enschede", "00000001001770367000", "0153"),
            ("Gemeente Amersfoort", "00000001001855980000", "0307"),
            ("Gemeente Zaanstad", "00000001002069027000", "0479"),
            ("Gemeente Zwolle", "00000001001785973000", "0193"),
            ("Gemeente Leiden", "00000001001895076000", "0546"),
            ("Gemeente Dordrecht", "00000001001927948000", "0505"),
            ("Gemeente Zoetermeer", "00000001001907345000", "0637"),
            ("Gemeente Deventer", "00000001001820445000", "0150"),
            ("Gemeente Delft", "00000001001907101000", "0503"),
            ("Gemeente Venlo", "00000001001834544000", "0983"),
            ("Gemeente Leeuwarden", "00000001001700399000", "0080"),
            ("Gemeente Alkmaar", "00000001002092782000", "0361"),
            ("Gemeente Helmond", "00000001001903450000", "0794"),
            ("Gemeente Hilversum", "00000001001822956000", "0402"),
            ("Gemeente Oss", "00000001001972226000", "0828"),
            ("Gemeente Vlaardingen", "00000001001944560000", "0622"),
            ("Gemeente Schiedam", "00000001001945560000", "0606"),
        ]

        gemeenten = []
        for naam, oin, code in gemeente_data:
            org, _ = Organisatie.objects.get_or_create(
                naam=naam,
                defaults={
                    "type": Organisatie.Type.GEMEENTE,
                    "status": Organisatie.Status.ACTIEF,
                    "oin": oin,
                    "bevoegd_gezag_code": code,
                    "website": f"https://www.{naam.lower().replace('gemeente ', '')}.nl",
                    "beschrijving": f"{naam} is een Nederlandse gemeente.",
                },
            )
            gemeenten.append(org)

        leverancier_data = [
            (
                "Centric",
                "Centric levert IT-oplossingen voor de publieke sector, waaronder "
                "zaaksystemen, burgerzaken en financiele software.",
                "https://www.centric.eu",
            ),
            (
                "PinkRoccade Local Government",
                "PinkRoccade ontwikkelt software voor gemeentelijke dienstverlening, "
                "waaronder iNavigator en Civiqs.",
                "https://www.pinkroccade-localgovernment.nl",
            ),
            (
                "Atos",
                "Atos biedt ICT-diensten en software voor de publieke sector, "
                "inclusief e-Suite en Toptaak.",
                "https://www.atos.net",
            ),
            (
                "Decos",
                "Decos ontwikkelt software voor informatie- en documentmanagement, "
                "waaronder JOIN voor zaakgericht werken.",
                "https://www.decos.com",
            ),
            (
                "Open Webconcept",
                "Open Webconcept biedt open source oplossingen voor gemeentelijke "
                "websites en portalen op basis van WordPress.",
                "https://openwebconcept.nl",
            ),
            (
                "Dimpact",
                "Dimpact is een cooperatieve vereniging van gemeenten die gezamenlijk "
                "ICT-oplossingen ontwikkelt en beheert.",
                "https://www.dimpact.nl",
            ),
            (
                "Green Valley",
                "Green Valley ontwikkelt software voor vergunningen, toezicht en "
                "handhaving (VTH) en het omgevingsdomein.",
                "https://www.greenvalley.nl",
            ),
            (
                "Conxillium",
                "Conxillium levert financiele software en bedrijfsvoeringssystemen "
                "voor gemeenten.",
                "https://www.conxillium.nl",
            ),
            (
                "BCT",
                "BCT ontwikkelt Corsa voor document- en informatiemanagement bij "
                "overheidsinstellingen.",
                "https://www.bct.nl",
            ),
            (
                "Kodision",
                "Kodision levert low-code oplossingen voor gemeentelijke processen "
                "en zaakgericht werken.",
                "https://www.kodision.com",
            ),
            (
                "Procura",
                "Procura ontwikkelt burgerzakensoftware (BRP, reisdocumenten, "
                "rijbewijzen) voor gemeenten.",
                "https://www.procura.nl",
            ),
            (
                "Lost Lemon",
                "Lost Lemon ontwikkelt digitale formulieren en e-diensten voor "
                "gemeentelijke dienstverlening.",
                "https://www.lostlemon.nl",
            ),
            (
                "Yard",
                "Yard biedt digitale oplossingen voor overheidscommunicatie, "
                "inclusief websites en intranetten.",
                "https://www.yard.nl",
            ),
            (
                "Enable-U",
                "Enable-U ontwikkelt integratieplatformen en API-management voor "
                "gemeentelijke informatieketens.",
                "https://www.enable-u.com",
            ),
            (
                "Topicus",
                "Topicus levert ICT-oplossingen voor de publieke sector, waaronder "
                "de Suwinet-koppeling en sociaal domein software.",
                "https://www.topicus.nl",
            ),
        ]

        leveranciers = []
        for naam, beschrijving, website in leverancier_data:
            org, _ = Organisatie.objects.get_or_create(
                naam=naam,
                defaults={
                    "type": Organisatie.Type.LEVERANCIER,
                    "status": Organisatie.Status.ACTIEF,
                    "website": website,
                    "beschrijving": beschrijving,
                },
            )
            leveranciers.append(org)

        # Contactpersonen voor leveranciers
        for lev in leveranciers:
            if not lev.contactpersonen.exists():
                Contactpersoon.objects.create(
                    organisatie=lev,
                    naam=f"Accountmanager {lev.naam}",
                    email=f"info@{lev.naam.lower().replace(' ', '').replace('-', '')}.nl",
                    telefoon=f"+31 {random.randint(20, 79)} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}",
                    functie="Accountmanager Gemeenten",
                )

        # Samenwerkingsverbanden
        swv_data = [
            (
                "Drechtsteden",
                "Samenwerking tussen Dordrecht, Zwijndrecht, Sliedrecht, "
                "Hendrik-Ido-Ambacht, Alblasserdam en Papendrecht.",
            ),
            (
                "Metropoolregio Eindhoven",
                "Samenwerking van 21 gemeenten in Zuidoost-Brabant.",
            ),
            (
                "Gemeenschappelijke Regeling Peelgemeenten",
                "Samenwerking Asten, Deurne, Gemert-Bakel, Helmond, Laarbeek en Someren.",
            ),
            (
                "BSOB",
                "Belasting Samenwerking Oost-Brabant voor gemeentelijke belastingen.",
            ),
            (
                "VNSG",
                "Vereniging van Nederlandse gemeenten die SAP gebruiken.",
            ),
        ]

        swv = []
        for naam, beschrijving in swv_data:
            org, _ = Organisatie.objects.get_or_create(
                naam=naam,
                defaults={
                    "type": Organisatie.Type.SAMENWERKINGSVERBAND,
                    "status": Organisatie.Status.ACTIEF,
                    "beschrijving": beschrijving,
                },
            )
            swv.append(org)

        # Een concept-organisatie
        Organisatie.objects.get_or_create(
            naam="NieuweSoftware BV",
            defaults={
                "type": Organisatie.Type.LEVERANCIER,
                "status": Organisatie.Status.CONCEPT,
                "beschrijving": "Nieuwe leverancier, wacht op fiattering.",
            },
        )

        return gemeenten, leveranciers, swv

    # ──────────────────────────────────────────────────────────────
    # GEMMA-componenten
    # ──────────────────────────────────────────────────────────────

    def _create_gemma_componenten(self):
        # Hoofdcomponenten (applicatiecomponenten)
        hoofd_data = [
            ("Zaaksysteem", "GEMMA-AC-001", "Systeem voor zaakgericht werken en procesondersteuning."),
            ("Burgerzakensysteem", "GEMMA-AC-002", "Systeem voor BRP, burgerlijke stand en reisdocumenten."),
            ("Financieel systeem", "GEMMA-AC-003", "Financiele administratie, begroting en verantwoording."),
            ("Documentmanagementsysteem", "GEMMA-AC-004", "Opslaan, beheren en ontsluiten van documenten."),
            ("Websitesysteem", "GEMMA-AC-005", "Gemeentelijke website en portaal voor inwoners."),
            ("E-formulierensysteem", "GEMMA-AC-006", "Digitale formulieren voor aanvragen en meldingen."),
            ("Vergunning Toezicht Handhaving", "GEMMA-AC-007", "VTH-processen en omgevingsvergunningen."),
            ("Gegevensmagazijn", "GEMMA-AC-008", "Centraal gegevensmagazijn en datadistributie."),
            ("Sociaal domein suite", "GEMMA-AC-009", "WMO, Jeugdzorg en Participatiewet ondersteuning."),
            ("Belastingsysteem", "GEMMA-AC-010", "Gemeentelijke belastingen en WOZ."),
            ("Berichtenverkeer", "GEMMA-AC-011", "Uitwisseling van berichten via StUF en API's."),
            ("Midoffice", "GEMMA-AC-012", "Koppelvlak tussen front- en backoffice systemen."),
            ("Klantcontactsysteem", "GEMMA-AC-013", "Klantcontactcentrum en multichannel dienstverlening."),
            ("Geografisch informatiesysteem", "GEMMA-AC-014", "GIS en ruimtelijke data."),
            ("Archiveringsysteem", "GEMMA-AC-015", "Digitale archivering en preservering."),
            ("Identiteitsmanagementsysteem", "GEMMA-AC-016", "IAM, SSO en toegangsbeheer."),
            ("Subsidiesysteem", "GEMMA-AC-017", "Beheer van subsidieaanvragen en -toekenningen."),
            ("Parkeersysteem", "GEMMA-AC-018", "Parkeervergunningen en handhaving."),
            ("Vastgoedmanagementsysteem", "GEMMA-AC-019", "Gemeentelijk vastgoedbeheer."),
            ("Inkoopsysteem", "GEMMA-AC-020", "Inkoopprocessen en contractbeheer."),
        ]

        componenten = {}
        for naam, archimate_id, beschrijving in hoofd_data:
            comp, _ = GemmaComponent.objects.get_or_create(
                archimate_id=archimate_id,
                defaults={
                    "naam": naam,
                    "type": GemmaComponent.Type.APPLICATIE_COMPONENT,
                    "beschrijving": beschrijving,
                    "gemma_online_url": f"https://www.gemmaonline.nl/index.php/{naam.replace(' ', '_')}",
                },
            )
            componenten[naam] = comp

        # Subcomponenten (applicatieservices) onder Zaaksysteem
        sub_data = [
            ("Zaakafhandelservice", "GEMMA-AS-001", "Zaaksysteem", "Afhandeling van zaken en processen."),
            ("Zaakregistratieservice", "GEMMA-AS-002", "Zaaksysteem", "Registratie en opslag van zaken."),
            ("BRP-beheermodule", "GEMMA-AS-003", "Burgerzakensysteem", "Beheer basisregistratie personen."),
            ("Burgerlijke stand module", "GEMMA-AS-004", "Burgerzakensysteem", "Akten burgerlijke stand."),
            ("Begrotingsmodule", "GEMMA-AS-005", "Financieel systeem", "Begroting en meerjarenraming."),
            ("Facturatiemodule", "GEMMA-AS-006", "Financieel systeem", "Factuurverwerking en debiteuren."),
            ("WMO-module", "GEMMA-AS-007", "Sociaal domein suite", "WMO aanvragen en toekenningen."),
            ("Jeugdzorgmodule", "GEMMA-AS-008", "Sociaal domein suite", "Jeugdzorg indicaties en trajecten."),
            ("WOZ-taxatiemodule", "GEMMA-AS-009", "Belastingsysteem", "WOZ waardebepalingen."),
            ("Omgevingsvergunningmodule", "GEMMA-AS-010", "Vergunning Toezicht Handhaving", "Omgevingsvergunningaanvragen."),
        ]

        for naam, archimate_id, parent_naam, beschrijving in sub_data:
            parent = componenten.get(parent_naam)
            comp, _ = GemmaComponent.objects.get_or_create(
                archimate_id=archimate_id,
                defaults={
                    "naam": naam,
                    "type": GemmaComponent.Type.APPLICATIE_SERVICE,
                    "beschrijving": beschrijving,
                    "parent": parent,
                    "gemma_online_url": f"https://www.gemmaonline.nl/index.php/{naam.replace(' ', '_')}",
                },
            )
            componenten[naam] = comp

        return componenten

    # ──────────────────────────────────────────────────────────────
    # Standaarden
    # ──────────────────────────────────────────────────────────────

    def _create_standaarden(self):
        standaard_data = [
            ("DigiD", "verplicht", "4.0", "Digitale identiteit voor burgers bij overheidsdiensten.",
             "https://www.forumstandaardisatie.nl/open-standaarden/digid"),
            ("StUF-BG", "verplicht", "3.10", "Standaard Uitwisseling Formaat voor basisgegevens.",
             "https://www.forumstandaardisatie.nl/open-standaarden/stuf"),
            ("StUF-ZKN", "verplicht", "3.10", "StUF koppelvlak voor zaak- en documentservices.",
             "https://www.forumstandaardisatie.nl/open-standaarden/stuf"),
            ("ZGW API's", "verplicht", "1.5", "Zaakgericht werken API-standaarden (ZRC, DRC, ZTC, BRC).",
             "https://www.forumstandaardisatie.nl/open-standaarden/zgw-apis"),
            ("CMIS", "aanbevolen", "1.1", "Content Management Interoperability Services voor documentuitwisseling.",
             "https://www.forumstandaardisatie.nl/open-standaarden/cmis"),
            ("SAML", "verplicht", "2.0", "Security Assertion Markup Language voor single sign-on.",
             "https://www.forumstandaardisatie.nl/open-standaarden/saml"),
            ("OAuth 2.0", "aanbevolen", "2.1", "Autorisatieprotocol voor API-toegang.",
             "https://www.forumstandaardisatie.nl/open-standaarden/oauth"),
            ("NEN 2082", "verplicht", "2023", "Norm voor duurzame toegankelijkheid van informatie.",
             "https://www.forumstandaardisatie.nl/open-standaarden/nen-2082"),
            ("OWMS", "verplicht", "4.0", "Overheid.nl Web Metadata Standaard.",
             "https://www.forumstandaardisatie.nl/open-standaarden/owms"),
            ("Haal Centraal BRP", "aanbevolen", "2.0", "API voor het bevragen van de BRP.",
             "https://www.forumstandaardisatie.nl/open-standaarden/haal-centraal"),
            ("OpenAPI Specification", "aanbevolen", "3.1", "Standaard voor het beschrijven van REST API's.",
             "https://www.forumstandaardisatie.nl/open-standaarden/openapi"),
            ("WCAG", "verplicht", "2.1", "Web Content Accessibility Guidelines voor digitale toegankelijkheid.",
             "https://www.forumstandaardisatie.nl/open-standaarden/wcag"),
            ("TLS", "verplicht", "1.3", "Transport Layer Security voor beveiligde communicatie.",
             "https://www.forumstandaardisatie.nl/open-standaarden/tls"),
            ("HTTPS/HSTS", "verplicht", "1.0", "Veilige verbindingen met HTTP Strict Transport Security.",
             "https://www.forumstandaardisatie.nl/open-standaarden/https-en-hsts"),
            ("IPv6", "verplicht", "6", "Internet Protocol versie 6.",
             "https://www.forumstandaardisatie.nl/open-standaarden/ipv6"),
            ("Archimate", "aanbevolen", "3.2", "Modelleertaal voor enterprise architectuur.",
             "https://www.forumstandaardisatie.nl/open-standaarden/archimate"),
            ("BPMN", "aanbevolen", "2.0", "Business Process Model and Notation voor procesbeschrijving.",
             "https://www.forumstandaardisatie.nl/open-standaarden/bpmn"),
            ("GML", "verplicht", "3.2", "Geography Markup Language voor geo-informatie.",
             "https://www.forumstandaardisatie.nl/open-standaarden/gml"),
        ]

        standaarden = {}
        for naam, type_str, versie, beschrijving, url in standaard_data:
            type_map = {
                "verplicht": Standaard.Type.VERPLICHT,
                "aanbevolen": Standaard.Type.AANBEVOLEN,
                "optioneel": Standaard.Type.OPTIONEEL,
            }
            std, _ = Standaard.objects.get_or_create(
                naam=naam,
                defaults={
                    "type": type_map[type_str],
                    "versie": versie,
                    "beschrijving": beschrijving,
                    "forum_standaardisatie_url": url,
                },
            )
            standaarden[naam] = std

        return standaarden

    # ──────────────────────────────────────────────────────────────
    # Gebruikers
    # ──────────────────────────────────────────────────────────────

    def _create_users(self, gemeenten, leveranciers):
        users = {}

        # Functioneel beheerder (VNG Realisatie)
        u, created = User.objects.get_or_create(
            email="admin@vngrealisatie.nl",
            defaults={
                "naam": "Lisa de Vries",
                "rol": User.Rol.FUNCTIONEEL_BEHEERDER,
                "status": User.Status.ACTIEF,
                "totp_enabled": False,
            },
        )
        if created:
            u.set_password("Welkom01!")
            u.save()
        users["admin"] = u

        # Gebruik-beheerders voor een aantal gemeenten
        gemeente_users = [
            ("j.jansen@utrecht.nl", "Jan Jansen", 0),
            ("m.bakker@amsterdam.nl", "Maria Bakker", 1),
            ("p.devries@rotterdam.nl", "Pieter de Vries", 2),
            ("s.meijer@denhaag.nl", "Sophie Meijer", 3),
            ("r.degraaf@eindhoven.nl", "Rick de Graaf", 4),
            ("a.vandijk@groningen.nl", "Anneke van Dijk", 5),
            ("t.mulder@tilburg.nl", "Tom Mulder", 6),
            ("k.visser@almere.nl", "Karin Visser", 7),
        ]

        for email, naam, idx in gemeente_users:
            u, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "naam": naam,
                    "organisatie": gemeenten[idx],
                    "rol": User.Rol.GEBRUIK_BEHEERDER,
                    "status": User.Status.ACTIEF,
                    "totp_enabled": False,
                },
            )
            if created:
                u.set_password("Welkom01!")
                u.save()
            users[f"gemeente_{idx}"] = u

        # Aanbod-beheerders voor leveranciers
        lev_users = [
            ("verkoop@centric.eu", "Hans Centric", 0),
            ("sales@pinkroccade.nl", "Eva PinkRoccade", 1),
            ("contact@atos.net", "Frank Atos", 2),
            ("info@decos.com", "Wilma Decos", 3),
        ]

        for email, naam, idx in lev_users:
            u, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "naam": naam,
                    "organisatie": leveranciers[idx],
                    "rol": User.Rol.AANBOD_BEHEERDER,
                    "status": User.Status.ACTIEF,
                    "totp_enabled": False,
                },
            )
            if created:
                u.set_password("Welkom01!")
                u.save()
            users[f"leverancier_{idx}"] = u

        # Raadplegers
        for i, gem in enumerate(gemeenten[8:15]):
            u, created = User.objects.get_or_create(
                email=f"raadpleger{i}@{gem.naam.lower().replace('gemeente ', '')}.nl",
                defaults={
                    "naam": f"Raadpleger {gem.naam.replace('Gemeente ', '')}",
                    "organisatie": gem,
                    "rol": User.Rol.GEBRUIK_RAADPLEGER,
                    "status": User.Status.ACTIEF,
                },
            )
            if created:
                u.set_password("Welkom01!")
                u.save()

        # Een wachtende gebruiker
        u, created = User.objects.get_or_create(
            email="nieuw@leverancier.nl",
            defaults={
                "naam": "Nieuwkomer NV",
                "rol": User.Rol.AANBOD_BEHEERDER,
                "status": User.Status.WACHT_OP_FIATTERING,
            },
        )
        if created:
            u.set_password("Welkom01!")
            u.save()

        return users

    # ──────────────────────────────────────────────────────────────
    # Pakketten
    # ──────────────────────────────────────────────────────────────

    def _create_pakketten(self, leveranciers, users):
        lev = {lev_obj.naam: lev_obj for lev_obj in leveranciers}

        pakket_data = [
            # (naam, versie, leverancier, licentievorm, beschrijving, website, cloud_provider, status)
            ("Suite4Gemeenten", "5.2", "Centric", "saas",
             "Integraal zaaksysteem voor gemeentelijke processen. Ondersteunt zaakgericht werken, "
             "documentmanagement en klantcontact.",
             "https://www.centric.eu/suite4gemeenten", "Microsoft Azure", "actief"),
            ("Key2Burgerzaken", "8.1", "Centric", "saas",
             "Burgerzakensoftware voor BRP-beheer, burgerlijke stand, reisdocumenten en rijbewijzen.",
             "https://www.centric.eu/key2burgerzaken", "Microsoft Azure", "actief"),
            ("Key2Financien", "7.5", "Centric", "saas",
             "Financieel systeem voor gemeenten met begroting, boekhouding en verantwoording.",
             "https://www.centric.eu/key2financien", "Microsoft Azure", "actief"),
            ("iNavigator", "4.3", "PinkRoccade Local Government", "commercieel",
             "Zaaksysteem en midoffice-oplossing voor gemeenten met procesondersteuning.",
             "https://www.pinkroccade-localgovernment.nl/inavigator", "", "actief"),
            ("Civiqs", "3.0", "PinkRoccade Local Government", "saas",
             "Platform voor digitale dienstverlening aan inwoners en bedrijven.",
             "https://www.pinkroccade-localgovernment.nl/civiqs", "Microsoft Azure", "actief"),
            ("eBurgerzaken", "6.4", "PinkRoccade Local Government", "commercieel",
             "Software voor burgerzakenprocessen waaronder BRP, reisdocumenten en naturalisatie.",
             "https://www.pinkroccade-localgovernment.nl/eburgerzaken", "", "actief"),
            ("Straatbeeld", "2.1", "PinkRoccade Local Government", "commercieel",
             "Oplossing voor beheer openbare ruimte en meldingen.",
             "https://www.pinkroccade-localgovernment.nl/straatbeeld", "", "actief"),
            ("e-Suite", "10.2", "Atos", "saas",
             "Integraal platform voor zaakgericht werken, documentmanagement en workflowbeheer.",
             "https://www.atos.net/e-suite", "Microsoft Azure", "actief"),
            ("Toptaak", "5.0", "Atos", "saas",
             "Website-platform gebaseerd op de toptaken-methodiek voor gemeentelijke websites.",
             "https://www.atos.net/toptaak", "Microsoft Azure", "actief"),
            ("JOIN", "2024.1", "Decos", "saas",
             "Zaakgericht werken, documentmanagement en besluitvorming in een platform.",
             "https://www.decos.com/join", "Microsoft Azure", "actief"),
            ("OpenZaak", "1.12", "Dimpact", "open_source",
             "Open source zaakregistratiecomponent conform ZGW API-standaarden.",
             "https://openzaak.org", "", "actief"),
            ("Open Notificaties", "1.5", "Dimpact", "open_source",
             "Open source component voor notificatie-routering conform NLX.",
             "https://github.com/open-zaak/open-notificaties", "", "actief"),
            ("OpenFormulieren", "2.6", "Dimpact", "open_source",
             "Open source platform voor het bouwen van digitale formulieren.",
             "https://open-formulieren.nl", "", "actief"),
            ("OpenKlant", "0.8", "Dimpact", "open_source",
             "Open source klantregistratiecomponent voor klantcontactbeheer.",
             "https://github.com/maykinmedia/open-klant", "", "actief"),
            ("OpenWoo", "1.2", "Open Webconcept", "open_source",
             "WordPress-plugin voor publicatie conform de Wet open overheid.",
             "https://openwebconcept.nl/openwoo", "", "actief"),
            ("Squit XO", "4.8", "Green Valley", "commercieel",
             "Vergunning-, toezicht- en handhavingssysteem voor het omgevingsdomein.",
             "https://www.greenvalley.nl/squit-xo", "", "actief"),
            ("GBI Geo", "3.4", "Green Valley", "commercieel",
             "Geo-informatiesysteem voor beheer openbare ruimte en vastgoedinformatie.",
             "https://www.greenvalley.nl/gbi", "", "actief"),
            ("Civision Financien", "9.1", "Conxillium", "commercieel",
             "Financieel systeem voor gemeentelijke begroting en verantwoording.",
             "https://www.conxillium.nl", "", "actief"),
            ("Corsa", "22.2", "BCT", "saas",
             "Document- en informatiemanagement voor overheidsorganisaties.",
             "https://www.bct.nl/corsa", "Microsoft Azure", "actief"),
            ("Rx.Mission", "3.5", "Kodision", "saas",
             "Low-code zaakafhandelplatform voor gemeentelijke processen.",
             "https://www.kodision.com/rxmission", "Microsoft Azure", "actief"),
            ("Procura BRP", "2024.2", "Procura", "commercieel",
             "Compleet burgerzakensysteem voor BRP, reisdocumenten en burgerlijke stand.",
             "https://www.procura.nl/producten/brp", "", "actief"),
            ("SmartForms", "5.1", "Lost Lemon", "saas",
             "Platform voor intelligente digitale formulieren en e-dienstverlening.",
             "https://www.lostlemon.nl/smartforms", "Microsoft Azure", "actief"),
            ("Drupal Govplatform", "10.3", "Yard", "open_source",
             "Drupal-gebaseerd platform voor gemeentelijke websites conform Gebruiker Centraal.",
             "https://www.yard.nl/govplatform", "", "actief"),
            ("Inzender", "2.3", "Enable-U", "saas",
             "Integratieplatform voor gegevensuitwisseling in de gemeentelijke informatieketen.",
             "https://www.enable-u.com/inzender", "Microsoft Azure", "actief"),
            ("Suwinet Inkijk", "8.0", "Topicus", "saas",
             "Inzageapplicatie voor gegevensuitwisseling binnen het sociaal domein (SUWI).",
             "https://www.topicus.nl/suwinet", "", "actief"),
            ("GWS4all", "12.0", "Centric", "saas",
             "Sociaal domein suite voor WMO, Jeugdwet en Participatiewet.",
             "https://www.centric.eu/gws4all", "Microsoft Azure", "actief"),
            ("Neuron ESB", "6.7", "Enable-U", "saas",
             "Enterprise service bus voor gemeentelijk berichtenverkeer.",
             "https://www.enable-u.com/neuron", "Microsoft Azure", "actief"),
            ("Centric Belastingen", "4.3", "Centric", "saas",
             "Belastingapplicatie voor OZB, rioolheffing en overige gemeentelijke belastingen.",
             "https://www.centric.eu/belastingen", "Microsoft Azure", "actief"),
            # Concept en verouderd
            ("NieuwePakket Beta", "0.1", "Kodision", "saas",
             "Nieuw pakket in ontwikkeling, nog niet beschikbaar voor productie.",
             "https://www.kodision.com/beta", "", "concept"),
            ("LegacyZaak", "2.0", "Atos", "commercieel",
             "Verouderd zaaksysteem, wordt niet meer actief onderhouden.",
             "", "", "verouderd"),
        ]

        licentie_map = {
            "commercieel": Pakket.Licentievorm.COMMERCIEEL,
            "open_source": Pakket.Licentievorm.OPEN_SOURCE,
            "saas": Pakket.Licentievorm.SAAS,
            "anders": Pakket.Licentievorm.ANDERS,
        }
        status_map = {
            "actief": Pakket.Status.ACTIEF,
            "concept": Pakket.Status.CONCEPT,
            "verouderd": Pakket.Status.VEROUDERD,
            "ingetrokken": Pakket.Status.INGETROKKEN,
        }

        pakketten = {}
        for naam, versie, lev_naam, lic, beschrijving, website, cloud, status in pakket_data:
            leverancier = lev.get(lev_naam)
            if not leverancier:
                continue
            open_source_lic = ""
            if lic == "open_source":
                open_source_lic = random.choice(["EUPL-1.2", "MIT", "Apache-2.0"])

            p, _ = Pakket.objects.get_or_create(
                naam=naam,
                leverancier=leverancier,
                defaults={
                    "versie": versie,
                    "status": status_map[status],
                    "beschrijving": beschrijving,
                    "licentievorm": licentie_map[lic],
                    "open_source_licentie": open_source_lic,
                    "website_url": website,
                    "cloud_provider": cloud,
                    "geregistreerd_door": users.get("admin"),
                },
            )
            pakketten[naam] = p

        return pakketten

    # ──────────────────────────────────────────────────────────────
    # Pakket-standaarden
    # ──────────────────────────────────────────────────────────────

    def _create_pakket_standaarden(self, pakketten, standaarden):
        # Welke pakketten ondersteunen welke standaarden
        koppelingen = {
            "Suite4Gemeenten": ["DigiD", "StUF-BG", "StUF-ZKN", "ZGW API's", "CMIS", "SAML", "WCAG", "TLS", "HTTPS/HSTS"],
            "Key2Burgerzaken": ["DigiD", "StUF-BG", "Haal Centraal BRP", "SAML", "TLS", "HTTPS/HSTS"],
            "Key2Financien": ["SAML", "TLS", "HTTPS/HSTS", "WCAG"],
            "iNavigator": ["StUF-BG", "StUF-ZKN", "ZGW API's", "CMIS", "DigiD", "SAML", "TLS"],
            "Civiqs": ["DigiD", "WCAG", "TLS", "HTTPS/HSTS", "OpenAPI Specification"],
            "eBurgerzaken": ["DigiD", "StUF-BG", "Haal Centraal BRP", "SAML", "TLS"],
            "e-Suite": ["ZGW API's", "StUF-ZKN", "CMIS", "DigiD", "SAML", "WCAG", "TLS", "HTTPS/HSTS"],
            "Toptaak": ["WCAG", "OWMS", "TLS", "HTTPS/HSTS", "IPv6"],
            "JOIN": ["ZGW API's", "CMIS", "StUF-ZKN", "DigiD", "SAML", "WCAG", "TLS"],
            "OpenZaak": ["ZGW API's", "OpenAPI Specification", "TLS", "HTTPS/HSTS", "OAuth 2.0"],
            "Open Notificaties": ["ZGW API's", "OpenAPI Specification", "TLS"],
            "OpenFormulieren": ["DigiD", "ZGW API's", "OpenAPI Specification", "WCAG", "TLS", "HTTPS/HSTS"],
            "OpenKlant": ["ZGW API's", "OpenAPI Specification", "TLS"],
            "Squit XO": ["StUF-BG", "StUF-ZKN", "DigiD", "SAML", "TLS"],
            "Corsa": ["CMIS", "NEN 2082", "StUF-ZKN", "SAML", "TLS", "HTTPS/HSTS"],
            "Rx.Mission": ["ZGW API's", "DigiD", "OpenAPI Specification", "WCAG", "TLS"],
            "SmartForms": ["DigiD", "WCAG", "TLS", "HTTPS/HSTS", "OpenAPI Specification"],
            "Drupal Govplatform": ["WCAG", "OWMS", "TLS", "HTTPS/HSTS", "IPv6"],
            "Inzender": ["StUF-BG", "StUF-ZKN", "ZGW API's", "TLS", "OpenAPI Specification"],
            "Neuron ESB": ["StUF-BG", "StUF-ZKN", "ZGW API's", "TLS", "OpenAPI Specification"],
            "Suwinet Inkijk": ["SAML", "TLS", "HTTPS/HSTS"],
            "GWS4all": ["StUF-BG", "DigiD", "SAML", "TLS", "HTTPS/HSTS"],
            "Centric Belastingen": ["StUF-BG", "DigiD", "SAML", "TLS"],
            "Procura BRP": ["StUF-BG", "Haal Centraal BRP", "DigiD", "SAML", "TLS"],
            "GBI Geo": ["GML", "TLS"],
            "Civision Financien": ["SAML", "TLS", "HTTPS/HSTS"],
            "OpenWoo": ["WCAG", "OWMS", "TLS", "HTTPS/HSTS"],
        }

        for pakket_naam, standaard_namen in koppelingen.items():
            pakket = pakketten.get(pakket_naam)
            if not pakket:
                continue
            for std_naam in standaard_namen:
                standaard = standaarden.get(std_naam)
                if not standaard:
                    continue
                PakketStandaard.objects.get_or_create(
                    pakket=pakket,
                    standaard=standaard,
                    defaults={"ondersteund": True},
                )

    # ──────────────────────────────────────────────────────────────
    # Pakket-GEMMA koppelingen
    # ──────────────────────────────────────────────────────────────

    def _create_pakket_gemma(self, pakketten, componenten):
        gemma_koppelingen = {
            "Suite4Gemeenten": ["Zaaksysteem", "Zaakafhandelservice", "Zaakregistratieservice", "Midoffice", "Klantcontactsysteem"],
            "Key2Burgerzaken": ["Burgerzakensysteem", "BRP-beheermodule", "Burgerlijke stand module"],
            "Key2Financien": ["Financieel systeem", "Begrotingsmodule", "Facturatiemodule"],
            "iNavigator": ["Zaaksysteem", "Midoffice", "Zaakafhandelservice"],
            "Civiqs": ["Websitesysteem", "E-formulierensysteem", "Klantcontactsysteem"],
            "eBurgerzaken": ["Burgerzakensysteem", "BRP-beheermodule", "Burgerlijke stand module"],
            "e-Suite": ["Zaaksysteem", "Documentmanagementsysteem", "Zaakafhandelservice", "Zaakregistratieservice"],
            "Toptaak": ["Websitesysteem"],
            "JOIN": ["Zaaksysteem", "Documentmanagementsysteem", "Zaakafhandelservice"],
            "OpenZaak": ["Zaaksysteem", "Zaakregistratieservice"],
            "Open Notificaties": ["Berichtenverkeer"],
            "OpenFormulieren": ["E-formulierensysteem"],
            "OpenKlant": ["Klantcontactsysteem"],
            "Squit XO": ["Vergunning Toezicht Handhaving", "Omgevingsvergunningmodule"],
            "Corsa": ["Documentmanagementsysteem", "Archiveringsysteem"],
            "Rx.Mission": ["Zaaksysteem", "Zaakafhandelservice"],
            "SmartForms": ["E-formulierensysteem"],
            "Drupal Govplatform": ["Websitesysteem"],
            "Inzender": ["Berichtenverkeer", "Midoffice"],
            "Neuron ESB": ["Berichtenverkeer", "Midoffice", "Gegevensmagazijn"],
            "Suwinet Inkijk": ["Sociaal domein suite"],
            "GWS4all": ["Sociaal domein suite", "WMO-module", "Jeugdzorgmodule"],
            "Centric Belastingen": ["Belastingsysteem", "WOZ-taxatiemodule"],
            "Procura BRP": ["Burgerzakensysteem", "BRP-beheermodule"],
            "GBI Geo": ["Geografisch informatiesysteem"],
            "Civision Financien": ["Financieel systeem", "Begrotingsmodule"],
            "OpenWoo": ["Websitesysteem"],
            "Straatbeeld": ["Geografisch informatiesysteem"],
        }

        for pakket_naam, comp_namen in gemma_koppelingen.items():
            pakket = pakketten.get(pakket_naam)
            if not pakket:
                continue
            for comp_naam in comp_namen:
                component = componenten.get(comp_naam)
                if not component:
                    continue
                PakketGemmaComponent.objects.get_or_create(
                    pakket=pakket,
                    gemma_component=component,
                )

    # ──────────────────────────────────────────────────────────────
    # Pakketgebruik en koppelingen
    # ──────────────────────────────────────────────────────────────

    def _create_pakketgebruik(self, pakketten, gemeenten, swv):
        """Wijs pakketten realistisch toe aan gemeenten."""
        random.seed(42)  # Reproduceerbaar

        # Standaard-stacks per "type" gemeente
        # Grote gemeenten: Centric of PinkRoccade stack
        centric_stack = [
            "Suite4Gemeenten", "Key2Burgerzaken", "Key2Financien",
            "GWS4all", "Centric Belastingen",
        ]
        pink_stack = [
            "iNavigator", "eBurgerzaken", "Civiqs", "Straatbeeld",
        ]
        # Aanvullende pakketten die gemeenten combineren
        aanvullingen = [
            "Corsa", "Squit XO", "SmartForms", "Neuron ESB",
            "Suwinet Inkijk", "OpenFormulieren", "OpenZaak",
            "Drupal Govplatform", "Toptaak", "Inzender",
            "GBI Geo", "JOIN", "e-Suite", "Rx.Mission",
            "OpenWoo", "Open Notificaties", "OpenKlant",
            "Civision Financien", "Procura BRP",
        ]

        alle_gebruik = {}

        for i, gemeente in enumerate(gemeenten):
            # Eerste helft gemeenten: Centric, tweede helft: PinkRoccade
            if i % 2 == 0:
                basis = centric_stack
            else:
                basis = pink_stack

            # Voeg 3-6 extra pakketten toe
            extra = random.sample(aanvullingen, k=random.randint(3, 6))
            pakket_namen = list(set(basis + extra))

            for pakket_naam in pakket_namen:
                pakket = pakketten.get(pakket_naam)
                if not pakket or pakket.status != Pakket.Status.ACTIEF:
                    continue

                start = date(2018, 1, 1) + timedelta(days=random.randint(0, 2000))
                status = random.choices(
                    [PakketGebruik.Status.IN_GEBRUIK, PakketGebruik.Status.GEPLAND],
                    weights=[90, 10],
                )[0]

                pg, created = PakketGebruik.objects.get_or_create(
                    pakket=pakket,
                    organisatie=gemeente,
                    defaults={
                        "status": status,
                        "start_datum": start,
                        "notitie": "",
                    },
                )
                key = f"{gemeente.naam}_{pakket_naam}"
                alle_gebruik[key] = pg

        # Samenwerkingsverbanden
        for s in swv:
            for pakket_naam in random.sample(list(pakketten.keys()), k=3):
                pakket = pakketten.get(pakket_naam)
                if not pakket or pakket.status != Pakket.Status.ACTIEF:
                    continue
                pg, _ = PakketGebruik.objects.get_or_create(
                    pakket=pakket,
                    organisatie=s,
                    defaults={
                        "status": PakketGebruik.Status.IN_GEBRUIK,
                        "start_datum": date(2021, 6, 1),
                    },
                )
                key = f"{s.naam}_{pakket_naam}"
                alle_gebruik[key] = pg

        # Koppelingen tussen pakketten (bij dezelfde gemeente)
        koppeling_templates = [
            ("Suite4Gemeenten", "Key2Burgerzaken", "api", "BRP-gegevens ophalen vanuit zaaksysteem."),
            ("Suite4Gemeenten", "Key2Financien", "api", "Financiele afhandeling van zaken."),
            ("Suite4Gemeenten", "Corsa", "api", "Documentopslag en -ontsluiting."),
            ("Suite4Gemeenten", "Neuron ESB", "api", "Berichtenverkeer via ESB."),
            ("iNavigator", "eBurgerzaken", "api", "BRP-gegevens ophalen vanuit zaaksysteem."),
            ("iNavigator", "Corsa", "api", "Documentopslag vanuit zaaksysteem."),
            ("OpenZaak", "OpenFormulieren", "api", "Formulierinzendingen als zaak registreren."),
            ("OpenZaak", "Open Notificaties", "api", "Notificaties bij zaakstatuswijzigingen."),
            ("OpenZaak", "OpenKlant", "api", "Klantgegevens koppelen aan zaken."),
            ("Neuron ESB", "Key2Burgerzaken", "api", "BRP-bevraging via ESB."),
            ("Neuron ESB", "Suwinet Inkijk", "api", "SUWI-gegevens ophalen."),
            ("GWS4all", "Suwinet Inkijk", "api", "Sociaal domein gegevensuitwisseling."),
            ("Squit XO", "Neuron ESB", "api", "VTH-berichten via ESB."),
            ("Civiqs", "eBurgerzaken", "api", "Burgerzakenproducten in dienstverleningsportaal."),
            ("SmartForms", "Suite4Gemeenten", "api", "Formulierinzendingen als zaak registreren."),
        ]

        for van_naam, naar_naam, kop_type, beschrijving in koppeling_templates:
            type_map = {
                "api": Koppeling.Type.API,
                "bestand": Koppeling.Type.BESTAND,
                "database": Koppeling.Type.DATABASE,
            }
            # Maak koppeling bij gemeenten waar beide pakketten in gebruik zijn
            for gemeente in gemeenten[:15]:
                van_key = f"{gemeente.naam}_{van_naam}"
                naar_key = f"{gemeente.naam}_{naar_naam}"
                van_pg = alle_gebruik.get(van_key)
                naar_pg = alle_gebruik.get(naar_key)
                if van_pg and naar_pg:
                    Koppeling.objects.get_or_create(
                        van_pakket_gebruik=van_pg,
                        naar_pakket_gebruik=naar_pg,
                        defaults={
                            "type": type_map.get(kop_type, Koppeling.Type.API),
                            "beschrijving": beschrijving,
                        },
                    )

    # ──────────────────────────────────────────────────────────────
    # Content en notificaties
    # ──────────────────────────────────────────────────────────────

    def _create_content(self, users):
        admin = users.get("admin")

        paginas = [
            ("Over de Softwarecatalogus", "over-de-softwarecatalogus",
             "De Softwarecatalogus is het centrale platform waar Nederlandse gemeenten, "
             "samenwerkingsverbanden en leveranciers software-applicaties kunnen registreren, "
             "vergelijken en raadplegen. Het platform maakt deel uit van de VNG Realisatie "
             "dienstverlening en biedt inzicht in het ICT-landschap van de gemeentelijke overheid.\n\n"
             "## Wat kun je met de Softwarecatalogus?\n\n"
             "- **Aanbod raadplegen**: Doorzoek het aanbod van software voor gemeenten\n"
             "- **Gebruik inzien**: Bekijk welke gemeenten welke software gebruiken\n"
             "- **Gluren bij de buren**: Vergelijk je pakketlandschap met andere gemeenten\n"
             "- **GEMMA-architectuur**: Bekijk software in de context van de GEMMA-referentiearchitectuur\n"
             "- **Standaarden**: Controleer welke open standaarden worden ondersteund"),
            ("Veelgestelde vragen", "veelgestelde-vragen",
             "## Hoe registreer ik mijn organisatie?\n\n"
             "Ga naar de registratiepagina en vul het formulier in. Na fiattering door de "
             "beheerder krijgt u toegang.\n\n"
             "## Hoe voeg ik een pakket toe?\n\n"
             "Als aanbod-beheerder kunt u via het dashboard pakketten registreren. "
             "Het pakket verschijnt eerst als concept en wordt na controle gepubliceerd.\n\n"
             "## Wat is GEMMA?\n\n"
             "GEMMA staat voor GEMeentelijke Model Architectuur. Het is de "
             "referentiearchitectuur voor gemeenten, ontwikkeld door VNG Realisatie.\n\n"
             "## Hoe exporteer ik mijn pakketlandschap?\n\n"
             "Via het dashboard kunt u uw pakketoverzicht exporteren als CSV, Excel of "
             "ArchiMate Exchange (AMEFF) bestand."),
            ("Privacyverklaring", "privacyverklaring",
             "## Privacyverklaring Softwarecatalogus\n\n"
             "De Softwarecatalogus wordt beheerd door VNG Realisatie BV. Wij respecteren uw "
             "privacy en verwerken persoonsgegevens conform de AVG.\n\n"
             "### Welke gegevens verwerken wij?\n\n"
             "- Naam en e-mailadres van geregistreerde gebruikers\n"
             "- Organisatiegegevens\n"
             "- Gebruiksstatistieken (via Matomo, privacyvriendelijk)\n\n"
             "### Contact\n\n"
             "Voor vragen over privacy kunt u contact opnemen met de functionaris "
             "gegevensbescherming via privacy@vngrealisatie.nl."),
            ("Toegankelijkheid", "toegankelijkheid",
             "## Toegankelijkheidsverklaring\n\n"
             "De Softwarecatalogus voldoet aan de Web Content Accessibility Guidelines (WCAG) "
             "2.1 niveau AA, conform de eisen van digitoegankelijk.nl.\n\n"
             "### Wat hebben wij gedaan?\n\n"
             "- Alle pagina's zijn navigeerbaar met toetsenbord\n"
             "- Voldoende kleurcontrast op alle elementen\n"
             "- Screen reader compatibel\n"
             "- Duidelijke foutmeldingen en labels\n\n"
             "### Probleem melden\n\n"
             "Ervaart u een toegankelijkheidsprobleem? Neem contact op via "
             "toegankelijkheid@softwarecatalogus.nl."),
        ]

        for titel, slug, inhoud in paginas:
            Pagina.objects.get_or_create(
                slug=slug,
                defaults={
                    "titel": titel,
                    "inhoud": inhoud,
                    "gepubliceerd": True,
                    "auteur": admin,
                },
            )

        nieuwsberichten = [
            ("Softwarecatalogus 2.0 gelanceerd", "softwarecatalogus-2-gelanceerd",
             "De vernieuwde Softwarecatalogus is live! Ontdek de nieuwe functies.",
             "Vandaag lanceren wij de volledig vernieuwde Softwarecatalogus. Het platform is "
             "van de grond af opgebouwd met moderne technologie en biedt verbeterde "
             "zoekfunctionaliteit, GEMMA-integratie en een nieuw dashboard voor gemeenten.\n\n"
             "## Belangrijkste verbeteringen\n\n"
             "- Snellere zoekfunctie met Meilisearch\n"
             "- Interactieve GEMMA-architectuurkaart\n"
             "- Verbeterd dashboard voor pakketbeheer\n"
             "- Open API conform NL API Strategie\n"
             "- Volledig toegankelijk (WCAG 2.1 AA)",
             -30),
            ("ZGW API's nu als verplichte standaard", "zgw-apis-verplichte-standaard",
             "De ZGW API-standaarden zijn opgenomen op de 'pas toe of leg uit'-lijst.",
             "Het Forum Standaardisatie heeft de ZGW API-standaarden (Zaakgericht Werken) "
             "opgenomen op de lijst van verplichte standaarden. Dit betekent dat alle "
             "overheidsinstellingen deze standaarden moeten toepassen of uitleggen waarom "
             "zij dit niet doen.\n\n"
             "In de Softwarecatalogus kunt u per pakket zien of de ZGW API's worden ondersteund.",
             -20),
            ("Nieuwe GEMMA-componenten toegevoegd", "nieuwe-gemma-componenten",
             "Het GEMMA-model is bijgewerkt met nieuwe referentiecomponenten.",
             "VNG Realisatie heeft het GEMMA-referentiearchitectuurmodel bijgewerkt. "
             "Er zijn nieuwe applicatiecomponenten en -services toegevoegd die aansluiten "
             "bij de Omgevingswet en de Wet open overheid.\n\n"
             "De bijgewerkte componenten zijn direct beschikbaar in de Softwarecatalogus.",
             -10),
            ("Open source groeit bij gemeenten", "open-source-groeit",
             "Steeds meer gemeenten kiezen voor open source software.",
             "Uit de gegevens van de Softwarecatalogus blijkt dat het gebruik van open source "
             "software bij gemeenten het afgelopen jaar met 35% is gegroeid. Vooral OpenZaak, "
             "OpenFormulieren en OpenKlant worden breed ingezet.\n\n"
             "De trend sluit aan bij de Common Ground-principes van VNG.",
             -5),
        ]

        now = timezone.now()
        for titel, slug, samenvatting, inhoud, dagen in nieuwsberichten:
            Nieuwsbericht.objects.get_or_create(
                slug=slug,
                defaults={
                    "titel": titel,
                    "samenvatting": samenvatting,
                    "inhoud": inhoud,
                    "gepubliceerd": True,
                    "publicatie_datum": now + timedelta(days=dagen),
                    "auteur": admin,
                },
            )

        # Notificaties voor admin
        if admin:
            notificatie_data = [
                ("organisatie_aanvraag", "NieuweSoftware BV heeft een registratie aangevraagd als leverancier."),
                ("gebruiker_aanvraag", "Nieuwkomer NV wacht op fiattering als aanbod-beheerder."),
                ("pakket_concept", "Het pakket 'NieuwePakket Beta' is aangemaakt als concept."),
                ("systeem", "De GEMMA-componentenlijst is succesvol bijgewerkt."),
            ]
            for type_str, bericht in notificatie_data:
                Notificatie.objects.get_or_create(
                    user=admin,
                    type=type_str,
                    bericht=bericht,
                    defaults={"gelezen": False},
                )

    # ──────────────────────────────────────────────────────────────
    # TenderNed aanbestedingen
    # ──────────────────────────────────────────────────────────────

    def _create_aanbestedingen(self, gemeenten):
        """Laad demo-aanbestedingen vanuit TenderNed client."""
        try:
            from apps.aanbestedingen.client import TenderNedClient
            from apps.aanbestedingen.models import Aanbesteding
            from apps.aanbestedingen.tasks import _koppel_gemma, _koppel_organisatie

            client = TenderNedClient(demo_mode=True)
            aanbestedingen_data = client.haal_ict_aanbestedingen_op()

            for item in aanbestedingen_data:
                aanbesteding, created = Aanbesteding.objects.get_or_create(
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
                    _koppel_organisatie(aanbesteding)
                    _koppel_gemma(aanbesteding)

            count = Aanbesteding.objects.count()
            self.stdout.write(f"  {count} TenderNed aanbestedingen geladen")
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"  Aanbestedingen overgeslagen: {exc}"))

    # ──────────────────────────────────────────────────────────────
    # Samenvatting
    # ──────────────────────────────────────────────────────────────

    def _print_summary(self):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("SAMENVATTING")
        self.stdout.write("=" * 60)
        stats = [
            ("Organisaties", Organisatie.objects.count()),
            ("  - Gemeenten", Organisatie.objects.filter(type="gemeente").count()),
            ("  - Leveranciers", Organisatie.objects.filter(type="leverancier").count()),
            ("  - Samenwerkingsverbanden", Organisatie.objects.filter(type="samenwerkingsverband").count()),
            ("Gebruikers", User.objects.count()),
            ("GEMMA-componenten", GemmaComponent.objects.count()),
            ("Standaarden", Standaard.objects.count()),
            ("Pakketten", Pakket.objects.count()),
            ("  - Actief", Pakket.objects.filter(status="actief").count()),
            ("  - Concept", Pakket.objects.filter(status="concept").count()),
            ("  - Verouderd", Pakket.objects.filter(status="verouderd").count()),
            ("Pakketgebruik", PakketGebruik.objects.count()),
            ("Koppelingen", Koppeling.objects.count()),
            ("Pakket-standaarden", PakketStandaard.objects.count()),
            ("Pakket-GEMMA", PakketGemmaComponent.objects.count()),
            ("Pagina's", Pagina.objects.count()),
            ("Nieuwsberichten", Nieuwsbericht.objects.count()),
            ("Notificaties", Notificatie.objects.count()),
            ("Aanbestedingen (TenderNed)", __import__("apps.aanbestedingen.models", fromlist=["Aanbesteding"]).Aanbesteding.objects.count()),
        ]
        for label, count in stats:
            self.stdout.write(f"  {label}: {count}")
        self.stdout.write("=" * 60)
        self.stdout.write("\nInloggegevens (alle wachtwoorden: Welkom01!):")
        self.stdout.write("  Admin:           admin@vngrealisatie.nl")
        self.stdout.write("  Gemeente Utrecht: j.jansen@utrecht.nl")
        self.stdout.write("  Leverancier:     verkoop@centric.eu")
        self.stdout.write("=" * 60)
