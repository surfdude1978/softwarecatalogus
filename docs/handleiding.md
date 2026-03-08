# Handleiding Softwarecatalogus

**Versie:** 1.0
**Datum:** maart 2026
**Doelgroep:** Gemeenten, leveranciers, samenwerkingsverbanden en beheerders

---

## Inhoudsopgave

1. [Inleiding](#1-inleiding)
2. [Publieke catalogus — geen account nodig](#2-publieke-catalogus--geen-account-nodig)
3. [Inloggen en uitloggen](#3-inloggen-en-uitloggen)
4. [Gemeente / Samenwerkingsverband — Gebruik-beheerder](#4-gemeente--samenwerkingsverband--gebruik-beheerder)
   - 4.1 [Pakket toevoegen aan uw landschap](#41-pakket-toevoegen-aan-uw-landschap)
   - 4.2 [Pakketgebruik bewerken of verwijderen](#42-pakketgebruik-bewerken-of-verwijderen)
   - 4.3 [Koppelingen registreren](#43-koppelingen-registreren)
   - 4.4 [Architectuurkaart bekijken](#44-architectuurkaart-bekijken)
   - 4.5 [Pakketoverzicht exporteren](#45-pakketoverzicht-exporteren)
5. [Gemeente / Samenwerkingsverband — Gebruik-raadpleger](#5-gemeente--samenwerkingsverband--gebruik-raadpleger)
   - 5.1 [Eigen landschap inzien](#51-eigen-landschap-inzien)
   - 5.2 [Landschap andere gemeente bekijken](#52-landschap-andere-gemeente-bekijken)
6. [Leverancier — Aanbod-beheerder](#6-leverancier--aanbod-beheerder)
   - 6.1 [Nieuw pakket registreren](#61-nieuw-pakket-registreren)
   - 6.2 [Pakket bewerken](#62-pakket-bewerken)
   - 6.3 [Standaarden koppelen](#63-standaarden-koppelen)
7. [Functioneel beheerder (VNG Realisatie)](#7-functioneel-beheerder-vng-realisatie)
   - 7.1 [Organisaties beheren en fiatteren](#71-organisaties-beheren-en-fiatteren)
   - 7.2 [Gebruikers beheren](#72-gebruikers-beheren)
   - 7.3 [GEMMA-model importeren](#73-gemma-model-importeren)
8. [Registreren — nieuw account aanmaken](#8-registreren--nieuw-account-aanmaken)
9. [Profiel en beveiliging](#9-profiel-en-beveiliging)
10. [Demo-accounts voor testen](#10-demo-accounts-voor-testen)
11. [Veelgestelde vragen](#11-veelgestelde-vragen)

---

## 1. Inleiding

De **Softwarecatalogus** is een centraal platform voor Nederlandse gemeenten, samenwerkingsverbanden en leveranciers. Het platform biedt:

- Een **publieke catalogus** van softwarepakketten die bij gemeenten in gebruik zijn
- De mogelijkheid om het eigen **softwarelandschap** bij te houden ("welke pakketten gebruikt mijn gemeente?")
- Inzicht in het softwarelandschap van **andere gemeenten** ("gluren bij de buren")
- Koppeling aan de **GEMMA referentiearchitectuur** voor de Architectuurkaart
- Verwijzingen naar **actieve aanbestedingen** via TenderNed

### Gebruikersrollen

| Rol | Beschrijving |
|-----|-------------|
| **Anoniem / Publiek** | Raadplegen van de publieke catalogus; geen account nodig |
| **Gebruik-raadpleger** | Inzien van het pakketlandschap van de eigen en andere gemeenten |
| **Gebruik-beheerder** | Volledig beheer van het eigen pakketlandschap |
| **Aanbod-beheerder** | Pakketten registreren en beheren namens een leverancier |
| **Functioneel beheerder** | Volledige administratie van het platform (VNG Realisatie) |

---

## 2. Publieke catalogus — geen account nodig

De publieke catalogus is voor iedereen toegankelijk via **[http://localhost:3000](http://localhost:3000)** (of de productie-URL van uw omgeving). U hoeft geen account aan te maken om pakketten te zoeken en te bekijken.

### Pakketten zoeken

1. Ga naar **Pakketten** in het hoofdmenu.
2. Gebruik de **zoekbalk** bovenaan om op naam, leverancier of beschrijving te zoeken.
3. Gebruik de **filters** aan de linkerzijde om te verfijnen op:
   - Leverancier
   - GEMMA-component (bijv. Zaaksysteem, Burgerzakensysteem)
   - Licentievorm (commercieel, open source, SaaS)
   - Standaard (bijv. DigiD, StUF-BG, ZGW API's)
4. Klik op een pakket om de **detailpagina** te openen.

### Pakketdetailpagina

De detailpagina toont:
- Beschrijving en versie-informatie
- Leverancier met contactgegevens
- Ondersteunde standaarden en testrapporten
- Gekoppelde GEMMA-componenten
- Welke gemeenten dit pakket gebruiken
- Gerelateerde pakketten

### Organisaties bekijken

1. Ga naar **Organisaties** in het hoofdmenu.
2. Zoek op naam of filter op type (gemeente, leverancier, samenwerkingsverband).
3. Klik op een organisatie voor contactgegevens en een overzicht van gekoppelde pakketten.

### Standaarden bekijken

1. Ga naar **Standaarden** in het hoofdmenu.
2. Hier vindt u verplichte en aanbevolen open standaarden, met verwijzingen naar Forum Standaardisatie.

---

## 3. Inloggen en uitloggen

### Inloggen

1. Klik op **Inloggen** rechtsboven in de navigatiebalk.
2. Vul uw **e-mailadres** en **wachtwoord** in.
3. Klik op **Inloggen**.
4. Als **tweefactorauthenticatie (2FA)** voor uw account is ingesteld:
   - Open uw authenticator-app (bijv. Google Authenticator, Microsoft Authenticator of Authy).
   - Voer de **6-cijferige code** in die de app toont.
   - Klik op **Verifieer**.
5. Na succesvolle aanmelding wordt u doorgestuurd naar uw **dashboard**.

> **Wachtwoord vergeten?** Klik op de link "Wachtwoord vergeten?" op de inlogpagina. U ontvangt een herstelmail op het bij ons bekende e-mailadres.

### Uitloggen

Klik op uw naam of avatar rechtsboven en kies **Uitloggen**.

---

## 4. Gemeente / Samenwerkingsverband — Gebruik-beheerder

Als **gebruik-beheerder** beheert u het volledige softwarelandschap van uw organisatie: welke pakketten zijn in gebruik, welke zijn gepland, en welke koppelingen bestaan er tussen systemen.

### 4.1 Pakket toevoegen aan uw landschap

**Voorbeeld: Gemeente Utrecht voegt een pakket toe**

Jan Jansen is gebruik-beheerder bij Gemeente Utrecht. Zo voegt hij een pakket toe:

1. **Log in** met uw account (`j.jansen@utrecht.nl` / `Welkom01!` in de demo).
2. Ga in het dashboard naar **Mijn Landschap** (via het menu links of de navigatiebalk).
3. U ziet een overzicht van alle pakketten die Gemeente Utrecht momenteel heeft geregistreerd.
4. Klik op de knop **+ Pakket toevoegen**.
5. In het zoekvenster dat verschijnt:
   - Typ de naam van het pakket dat u wilt toevoegen, bijv. `Suite4Gemeenten`.
   - De lijst filtert direct op uw invoer.
   - Klik op het gewenste pakket om het te selecteren.
6. Vul de details in voor het gebruik van dit pakket:
   - **Status**: kies *In gebruik*, *Gepland* of *Gestopt*
   - **Startdatum** (optioneel): wanneer is het pakket in gebruik genomen?
   - **Einddatum** (optioneel): wanneer stopt het gebruik? (alleen bij status *Gestopt*)
   - **Notitie** (optioneel): aanvullende informatie, bijv. "Gebruikt door afdeling Burgerzaken"
7. Klik op **Opslaan**.

Het pakket verschijnt nu in uw landschapsoverzicht met de gekozen status.

> **Pakket niet gevonden?** Als het pakket nog niet in de catalogus staat, kunt u als gebruik-beheerder een **concept-pakket aanmaken**. Ga naar Pakketten → Nieuw pakket. Het pakket krijgt de status *Concept* en wordt zichtbaar na fiattering door de functioneel beheerder of de leverancier.

### 4.2 Pakketgebruik bewerken of verwijderen

1. Ga naar **Mijn Landschap**.
2. Zoek het pakket in de lijst of gebruik de zoekfunctie.
3. Klik op het **drie-puntjes-menu** (⋮) naast het pakket.
4. Kies **Bewerken** om status, datums of notities aan te passen, of **Verwijderen** om het pakket uit uw landschap te halen.

> **Let op:** verwijderen uit uw landschap verwijdert het pakket niet uit de catalogus. Het pakket blijft beschikbaar voor andere gemeenten.

### 4.3 Koppelingen registreren

Koppelingen geven aan dat twee systemen gegevens uitwisselen. Zo registreert u een koppeling:

1. Ga naar **Mijn Landschap**.
2. Klik op het pakket waarvandaan de koppeling vertrekt.
3. Open het tabblad **Koppelingen**.
4. Klik op **+ Koppeling toevoegen**.
5. Vul in:
   - **Naar pakket**: zoek en selecteer het doelpakket
   - **Type**: API, bestand of anders
   - **Beschrijving** (optioneel): wat wordt er uitgewisseld?
6. Klik op **Opslaan**.

Koppelingen worden ook zichtbaar in de **Architectuurkaart**.

### 4.4 Architectuurkaart bekijken

De architectuurkaart toont een visuele weergave van uw pakketlandschap, geplot op de GEMMA referentiearchitectuur.

1. Ga naar **Mijn Landschap → Architectuurkaart**.
2. De kaart toont de GEMMA-componenten (bijv. Zaaksysteem, Burgerzakensysteem) met de pakketten die u daaraan hebt gekoppeld.
3. **Legenda**:
   - 🟢 Groen = pakket is *in gebruik*
   - 🟡 Geel = pakket is *gepland*
   - 🔴 Rood = pakket is *gestopt*
4. Klik op een component of pakket voor meer details.
5. Gebruik de knoppen **+** en **-** om in en uit te zoomen, of versleep de kaart om te navigeren.

> **Tip:** De architectuurkaart biedt direct inzicht in lacunes — GEMMA-componenten zonder pakket zijn direct zichtbaar.

### 4.5 Pakketoverzicht exporteren

1. Ga naar **Mijn Landschap**.
2. Klik op de knop **Exporteren** (rechtsboven in het overzicht).
3. Kies het gewenste formaat:
   - **CSV** — geschikt voor Excel en andere spreadsheet-programma's
   - **Excel (.xlsx)** — direct te openen in Microsoft Excel
   - **AMEFF** — ArchiMate Exchange formaat, importeerbaar in Archi, BiZZdesign of Sparx EA
4. De download start automatisch.

---

## 5. Gemeente / Samenwerkingsverband — Gebruik-raadpleger

Als **gebruik-raadpleger** kunt u het pakketlandschap inzien, maar geen wijzigingen doorvoeren.

### 5.1 Eigen landschap inzien

1. Log in met uw account.
2. Ga naar **Mijn Landschap**.
3. U ziet een overzicht van alle geregistreerde pakketten van uw organisatie, inclusief status en koppelingen.

### 5.2 Landschap andere gemeente bekijken

Met de functie "gluren bij de buren" kunt u zien welke pakketten andere gemeenten gebruiken.

1. Ga naar **Organisaties** in het hoofdmenu.
2. Zoek de gewenste gemeente (bijv. "Amsterdam").
3. Klik op de organisatienaam.
4. Op de detailpagina ziet u onder het tabblad **Pakketlandschap** welke pakketten deze gemeente gebruikt.

> **Privacy:** gemeenten beheren zelf welke informatie zichtbaar is voor anderen. Sommige pakketten kunnen als niet-openbaar zijn gemarkeerd.

---

## 6. Leverancier — Aanbod-beheerder

Als **aanbod-beheerder** beheert u de pakketten die uw organisatie aanbiedt in de catalogus.

### 6.1 Nieuw pakket registreren

1. Log in met uw leveranciersaccount.
2. Ga naar **Aanbod** in het dashboard.
3. Klik op **+ Nieuw pakket**.
4. Vul het formulier in:
   - **Naam**: officiële productnaam
   - **Versie**: huidige versienummer
   - **Beschrijving**: wat doet het pakket? (minimaal 50 tekens aanbevolen)
   - **Licentievorm**: commercieel, open source, SaaS of anders
   - **Open source licentie** (als van toepassing): bijv. EUPL, MIT, GPL
   - **Website**: URL naar de productpagina
   - **Documentatie**: URL naar technische documentatie
   - **Cloud-provider** (optioneel): bijv. Microsoft Azure, AWS
   - **Contactpersoon**: wie is aanspreekpunt voor gemeenten?
5. Klik op **Opslaan**.

Het pakket wordt aangemaakt met de status **Concept**. Na controle door de functioneel beheerder wordt de status gewijzigd naar **Actief** en is het pakket zichtbaar in de publieke catalogus.

### 6.2 Pakket bewerken

1. Ga naar **Aanbod**.
2. Klik op het pakket dat u wilt bewerken.
3. Klik op de knop **Bewerken**.
4. Pas de gewenste velden aan.
5. Klik op **Opslaan**.

> **Let op:** wijzigingen aan een actief pakket zijn direct zichtbaar voor alle gebruikers.

### 6.3 Standaarden koppelen

Gemeenten zoeken actief op pakketten die bepaalde standaarden ondersteunen. Houd dit overzicht actueel:

1. Open de detailpagina van uw pakket via **Aanbod**.
2. Ga naar het tabblad **Standaarden**.
3. Klik op **+ Standaard toevoegen**.
4. Zoek en selecteer de standaard (bijv. DigiD, StUF-BG, ZGW API's).
5. Geef aan of de standaard **ondersteund** wordt.
6. Upload desgewenst een **testrapport** (PDF).
7. Klik op **Opslaan**.

---

## 7. Functioneel beheerder (VNG Realisatie)

De functioneel beheerder heeft toegang tot alle beheerfuncties van het platform.

### 7.1 Organisaties beheren en fiatteren

Wanneer een nieuwe organisatie zich registreert, krijgt deze de status **Concept**. De functioneel beheerder keurt deze goed:

1. Log in als functioneel beheerder (`admin@vngrealisatie.nl` in de demo).
2. Ga naar **Beheer → Organisaties**.
3. U ziet een lijst van alle organisaties. Filter op **Status: Concept** om nieuwe aanvragen te zien.
4. Klik op een organisatie om de ingediende gegevens te beoordelen.
5. Klik op **Fiatteren** om de organisatie te activeren, of **Afwijzen** met een toelichting.

Na fiattering ontvangen de gebruikers van de organisatie een bevestigingsmail.

### 7.2 Gebruikers beheren

1. Ga naar **Beheer → Gebruikers**.
2. U ziet een overzicht van alle gebruikers, gefilterd op rol en status.
3. Klik op een gebruiker om:
   - De **rol** te wijzigen
   - De **status** te wijzigen (actief / inactief / wacht op fiattering)
   - De **organisatiekoppeling** aan te passen

### 7.3 GEMMA-model importeren

De GEMMA architectuurkaart is gebaseerd op een ArchiMate-model. Als het GEMMA-model is bijgewerkt, kan de functioneel beheerder een nieuw model importeren:

1. Ga naar **Beheer → GEMMA**.
2. Klik op **AMEFF importeren**.
3. Selecteer het AMEFF-bestand (XML-formaat, te downloaden van GEMMA Online).
4. Klik op **Importeren starten**.
5. Het systeem verwerkt het bestand en rapporteert:
   - Nieuwe componenten toegevoegd
   - Bestaande componenten bijgewerkt
   - Eventuele conflicten (hernoemde componenten)
6. Bestaande koppelingen tussen pakketten en componenten blijven behouden.

---

## 8. Registreren — nieuw account aanmaken

### Nieuwe gebruiker bij een bestaande organisatie

Als uw organisatie (gemeente of leverancier) al in de catalogus staat:

1. Ga naar de **Inlogpagina** en klik op **Registreren**.
2. Vul in: naam, e-mailadres, wachtwoord.
3. Zoek en selecteer uw **organisatie**.
4. Klik op **Registreren**.
5. Uw account krijgt de status *Wacht op fiattering*. De beheerder van uw organisatie ontvangt een notificatie.
6. Na fiattering ontvangt u een welkomstmail en kunt u inloggen.

### Nieuwe organisatie registreren

Als uw organisatie nog niet in de catalogus staat:

1. Ga naar de **Inlogpagina** en klik op **Registreren**.
2. Klik op **Mijn organisatie staat er niet bij** of ga direct naar **/registreer/organisatie**.
3. Vul in:
   - Organisatienaam
   - Type (gemeente, leverancier, samenwerkingsverband)
   - OIN (indien gemeente of samenwerkingsverband)
   - Website
   - Uw persoonlijke gegevens (naam, e-mail, wachtwoord)
4. Klik op **Registreren**.
5. Uw organisatie krijgt de status *Concept*. De functioneel beheerder van VNG Realisatie beoordeelt de aanvraag.
6. Na fiattering kunt u inloggen en bent u automatisch de eerste beheerder van uw organisatie.

---

## 9. Profiel en beveiliging

### Profiel bewerken

1. Klik op uw naam of avatar rechtsboven.
2. Kies **Profiel** of ga naar **/profiel**.
3. U kunt uw naam en e-mailadres bijwerken.

### Wachtwoord wijzigen

1. Ga naar uw **Profiel**.
2. Klik op **Wachtwoord wijzigen**.
3. Vul uw huidige wachtwoord in, en daarna tweemaal het nieuwe wachtwoord.
4. Klik op **Opslaan**.

### Tweefactorauthenticatie (2FA) instellen

2FA is sterk aanbevolen voor alle accounts, en verplicht voor beheeraccounts.

1. Ga naar uw **Profiel**.
2. Klik op **2FA inschakelen**.
3. Scan de QR-code met uw authenticator-app (bijv. Google Authenticator, Microsoft Authenticator, Authy).
4. Voer de 6-cijferige code in die de app toont ter verificatie.
5. Klik op **Activeren**.

Vanaf nu wordt bij elke aanmelding een code uit uw authenticator-app gevraagd.

> **Authenticator-app kwijt?** Neem contact op met uw organisatiebeheerder of met VNG Realisatie (admin@vngrealisatie.nl) om uw 2FA te resetten.

---

## 10. Demo-accounts voor testen

De volgende accounts zijn beschikbaar in de demo-omgeving. **Alle accounts hebben wachtwoord `Welkom01!`** en hebben geen 2FA ingesteld.

| Rol | E-mailadres | Naam | Organisatie |
|-----|------------|------|-------------|
| Functioneel beheerder | `admin@vngrealisatie.nl` | Lisa de Vries | VNG Realisatie |
| Gebruik-beheerder | `j.jansen@utrecht.nl` | Jan Jansen | Gemeente Utrecht |
| Gebruik-beheerder | `m.bakker@amsterdam.nl` | Maria Bakker | Gemeente Amsterdam |
| Gebruik-beheerder | `p.devries@rotterdam.nl` | Pieter de Vries | Gemeente Rotterdam |
| Gebruik-beheerder | `s.meijer@denhaag.nl` | Sophie Meijer | Gemeente Den Haag |
| Gebruik-beheerder | `r.degraaf@eindhoven.nl` | Rick de Graaf | Gemeente Eindhoven |
| Aanbod-beheerder | `verkoop@centric.eu` | Hans Centric | Centric |
| Aanbod-beheerder | `sales@pinkroccade.nl` | Eva PinkRoccade | PinkRoccade Local Government |
| Aanbod-beheerder | `contact@atos.net` | Frank Atos | Atos |
| Aanbod-beheerder | `info@decos.com` | Wilma Decos | Decos |

> **Let op:** de demo-accounts zijn uitsluitend bedoeld voor test- en demonstratiedoeleinden.

---

## 11. Veelgestelde vragen

**Waarom zie ik mijn pakket niet in de catalogus?**
Nieuw geregistreerde pakketten krijgen eerst de status *Concept*. Ze zijn pas voor iedereen zichtbaar nadat de functioneel beheerder (of de leverancier zelf, bij aanbod-beheerders) de status heeft gewijzigd naar *Actief*.

**Kan ik een pakket toevoegen dat nog niet in de catalogus staat?**
Ja. Als gebruik-beheerder kunt u een **concept-pakket** aanmaken voor een ontbrekend pakket. Het pakket is dan zichtbaar in uw eigen landschap en wordt na review eventueel toegevoegd aan de publieke catalogus.

**Hoe weet ik welke standaarden een pakket ondersteunt?**
Op de detailpagina van elk pakket staat een tabblad **Standaarden** met een overzicht van ondersteunde (en niet-ondersteunde) standaarden, inclusief eventuele testrapporten.

**Kan ik zien welke andere gemeenten hetzelfde pakket gebruiken?**
Ja. Op de detailpagina van een pakket staat onder **Gebruik** een lijst van gemeenten die dit pakket in gebruik hebben. U hebt hiervoor minimaal de rol *Gebruik-raadpleger* nodig.

**Hoe exporteer ik mijn pakketlandschap voor gebruik in een architectuurtool?**
Gebruik de **AMEFF-export** (ArchiMate Exchange). Dit formaat is importeerbaar in tools zoals Archi (open source), BiZZdesign en Sparx Enterprise Architect. Zie [sectie 4.5](#45-pakketoverzicht-exporteren).

**Waar vind ik actieve aanbestedingen?**
Op de homepage en via het menu **TenderNed** vindt u een overzicht van lopende aanbestedingen die relevant zijn voor gemeentelijke software, rechtstreeks opgehaald vanuit TenderNed.

**Hoe neem ik contact op voor hulp?**
Neem contact op met VNG Realisatie via:
- E-mail: softwarecatalogus@vng.nl
- Of via de contactpagina op [https://www.vngrealisatie.nl](https://www.vngrealisatie.nl)

---

*Softwarecatalogus — ontwikkeld door VNG Realisatie | EUPL-1.2 licentie*
