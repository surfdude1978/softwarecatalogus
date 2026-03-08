/**
 * Handleiding-inhoud voor de in-app help.
 *
 * Elke sectie bevat:
 *  - id         unieke sleutel
 *  - groep      navigatiegroep (linker kolom)
 *  - titel      weergavenaam
 *  - routes     exacte paden waar deze sectie als primaire context geldt
 *  - routePrefixes  padprefixen (bijv. "/aanbod/" matcht ook /aanbod/123/bewerken)
 *  - zoekTermen extra zoekwoorden voor de zoekfunctie
 *  - inhoud     markdown-achtige tekst (ondersteund door MiniMarkdown)
 */

export interface HelpSectie {
  id: string;
  groep: string;
  titel: string;
  routes: string[];
  routePrefixes: string[];
  zoekTermen: string[];
  inhoud: string;
}

export const HELP_SECTIES: HelpSectie[] = [
  // ──────────────────────────────────────────────────
  // Algemeen
  // ──────────────────────────────────────────────────
  {
    id: "welkom",
    groep: "Algemeen",
    titel: "Welkom in de Softwarecatalogus",
    routes: ["/"],
    routePrefixes: [],
    zoekTermen: ["welkom", "introductie", "over", "platform", "vng"],
    inhoud: `## Wat is de Softwarecatalogus?

De Softwarecatalogus is het centrale platform van VNG Realisatie voor Nederlandse gemeenten, samenwerkingsverbanden en leveranciers.

**Wat kunt u doen?**

- **Zoeken** in honderden softwarepakketten zonder account
- **Vergelijken** welke gemeenten welke software gebruiken
- **Beheren** van uw eigen pakketlandschap (na inloggen)
- **Registreren** van pakketten als leverancier
- **Visualiseren** op de GEMMA architectuurkaart

> **Tip:** U kunt de publieke catalogus volledig raadplegen zonder in te loggen. Maak een account aan voor beheersfuncties.`,
  },

  {
    id: "publieke-catalogus",
    groep: "Algemeen",
    titel: "Pakketten zoeken & bekijken",
    routes: ["/pakketten", "/organisaties", "/standaarden"],
    routePrefixes: ["/pakketten/", "/organisaties/"],
    zoekTermen: [
      "zoeken",
      "filteren",
      "catalogus",
      "pakket",
      "leverancier",
      "standaard",
      "publiek",
      "anoniem",
    ],
    inhoud: `## Pakketten zoeken

1. Ga naar **Pakketten** in het menu
2. Typ in de zoekbalk: naam, leverancier of beschrijving
3. Gebruik de **filters** links om te verfijnen:
   - Licentievorm (commercieel, open source, SaaS)
   - GEMMA-component (bijv. Zaaksysteem)
   - Standaard (bijv. DigiD, StUF-BG)
4. Klik op een pakket voor de detailpagina

**Op de detailpagina ziet u:**
- Beschrijving en versie-informatie
- Ondersteunde standaarden en testrapporten
- Gekoppelde GEMMA-componenten
- Welke gemeenten het pakket gebruiken

> **Tip:** Zoeken werkt ook op afkorting — typ bijv. "DMS" voor documentmanagementsystemen.`,
  },

  {
    id: "inloggen",
    groep: "Algemeen",
    titel: "Inloggen en uitloggen",
    routes: ["/login"],
    routePrefixes: [],
    zoekTermen: [
      "inloggen",
      "login",
      "wachtwoord",
      "2fa",
      "totp",
      "authenticator",
      "uitloggen",
    ],
    inhoud: `## Inloggen

1. Klik op **Inloggen** rechtsboven
2. Vul uw **e-mailadres** en **wachtwoord** in
3. Klik op **Inloggen**
4. Als **tweefactorauthenticatie (2FA)** actief is:
   - Open uw authenticator-app (bijv. Google Authenticator)
   - Voer de **6-cijferige code** in
   - Klik **Verifieer**

**Wachtwoord vergeten?**
Klik op "Wachtwoord vergeten?" op de inlogpagina. U ontvangt een herstellink per e-mail.

## Demo-accounts (testomgeving)

| Rol | E-mail | Wachtwoord |
|---|---|---|
| Functioneel beheerder | admin@vngrealisatie.nl | Welkom01! |
| Gemeente Utrecht | j.jansen@utrecht.nl | Welkom01! |
| Leverancier Centric | verkoop@centric.eu | Welkom01! |`,
  },

  {
    id: "registreren",
    groep: "Algemeen",
    titel: "Registreren — nieuw account",
    routes: ["/registreer", "/registreer/organisatie"],
    routePrefixes: ["/registreer/"],
    zoekTermen: [
      "registreren",
      "account",
      "aanmaken",
      "organisatie",
      "nieuwe gebruiker",
      "fiattering",
    ],
    inhoud: `## Nieuwe gebruiker bij bestaande organisatie

1. Klik op **Registreren** op de inlogpagina
2. Vul naam, e-mailadres en wachtwoord in
3. Zoek en selecteer uw **organisatie**
4. Klik op **Registreren**
5. Uw account wacht op goedkeuring door de organisatiebeheerder

## Nieuwe organisatie registreren

1. Klik op **Mijn organisatie staat er niet bij**
2. Vul naam, type en contactgegevens in
3. De functioneel beheerder (VNG Realisatie) keurt de organisatie goed
4. Na goedkeuring bent u automatisch de eerste beheerder

> **Let op:** Concept-accounts en -organisaties zijn zichtbaar maar niet volledig functioneel totdat ze zijn goedgekeurd.`,
  },

  // ──────────────────────────────────────────────────
  // Gebruik-beheerder (gemeente)
  // ──────────────────────────────────────────────────
  {
    id: "mijn-landschap",
    groep: "Gemeente / SWV",
    titel: "Pakket toevoegen aan uw landschap",
    routes: ["/mijn-landschap"],
    routePrefixes: [],
    zoekTermen: [
      "pakket toevoegen",
      "landschap",
      "gebruik",
      "in gebruik",
      "gepland",
      "gestopt",
      "gemeente",
      "overzicht",
    ],
    inhoud: `## Pakket toevoegen aan uw landschap

1. Ga naar **Mijn Landschap** in het dashboard
2. Klik op **+ Pakket toevoegen**
3. Zoek het pakket op naam (bijv. "Suite4Gemeenten")
4. Klik op het pakket om het te selecteren
5. Vul de details in:
   - **Status:** In gebruik / Gepland / Gestopt
   - **Startdatum** (optioneel)
   - **Notitie** (optioneel, bijv. "gebruikt door afdeling Burgerzaken")
6. Klik op **Opslaan**

## Pakketgebruik bewerken of verwijderen

1. Klik op de **drie puntjes (⋮)** naast een pakket
2. Kies **Bewerken** of **Verwijderen**

> **Pakket niet gevonden?** Maak een concept-pakket aan via Pakketten → Nieuw pakket. Het wordt zichtbaar na fiattering.`,
  },

  {
    id: "koppelingen",
    groep: "Gemeente / SWV",
    titel: "Koppelingen registreren",
    routes: [],
    routePrefixes: [],
    zoekTermen: [
      "koppeling",
      "integratie",
      "api",
      "gegevensuitwisseling",
      "systemen",
      "verbinding",
    ],
    inhoud: `## Koppeling registreren tussen twee pakketten

1. Ga naar **Mijn Landschap**
2. Klik op het pakket waarvandaan de koppeling vertrekt
3. Open het tabblad **Koppelingen**
4. Klik op **+ Koppeling toevoegen**
5. Selecteer het doelpakket
6. Kies het type: API / bestand / anders
7. Voeg een beschrijving toe (optioneel)
8. Klik op **Opslaan**

Koppelingen zijn zichtbaar in de **Architectuurkaart** en in de exportbestanden.`,
  },

  {
    id: "architectuurkaart",
    groep: "Gemeente / SWV",
    titel: "Architectuurkaart (GEMMA)",
    routes: ["/mijn-landschap/architectuurkaart"],
    routePrefixes: [],
    zoekTermen: [
      "architectuurkaart",
      "gemma",
      "archimate",
      "kaart",
      "visualisatie",
      "component",
    ],
    inhoud: `## Architectuurkaart lezen

De kaart toont uw pakketten geplot op de GEMMA referentiearchitectuur.

**Kleurcodering:**
- 🟢 **Groen** — pakket is *in gebruik*
- 🟡 **Geel** — pakket is *gepland*
- 🔴 **Rood** — pakket is *gestopt*

**Navigeren:**
- Klik op een GEMMA-component voor details
- Klik op een pakket-badge om de detailpagina te openen
- Klik op de componentnaam voor de GEMMA Online definitie

> **Tip:** Componenten zonder pakket zijn direct zichtbaar als lacunes in uw ICT-landschap.

## Exporteren als AMEFF

Gebruik de **Exporteren**-knop op Mijn Landschap om uw landschap te downloaden als ArchiMate Exchange-bestand. Dit kunt u importeren in Archi, BiZZdesign of Sparx EA.`,
  },

  {
    id: "export",
    groep: "Gemeente / SWV",
    titel: "Pakketoverzicht exporteren",
    routes: [],
    routePrefixes: [],
    zoekTermen: [
      "exporteren",
      "download",
      "excel",
      "csv",
      "ameff",
      "archimate",
      "archi",
    ],
    inhoud: `## Exportformaten

Ga naar **Mijn Landschap** → knop **Exporteren** (rechtsboven):

- **Excel (.xlsx)** — direct te openen in Microsoft Excel
- **CSV** — voor andere spreadsheetprogramma's
- **AMEFF** — ArchiMate Exchange, importeerbaar in Archi of BiZZdesign

> **Tip:** Het AMEFF-bestand bevat uw pakketten, GEMMA-componenten én koppelingen — geschikt voor hergebruik in architectuurtools.`,
  },

  {
    id: "buren-bekijken",
    groep: "Gemeente / SWV",
    titel: "Landschap andere gemeente bekijken",
    routes: [],
    routePrefixes: [],
    zoekTermen: [
      "buren",
      "gluren",
      "andere gemeente",
      "vergelijken",
      "landschap bekijken",
    ],
    inhoud: `## "Gluren bij de buren"

1. Ga naar **Organisaties** in het hoofdmenu
2. Zoek de gewenste gemeente (bijv. "Amsterdam")
3. Klik op de organisatienaam
4. Open het tabblad **Pakketlandschap**

U ziet welke pakketten die gemeente gebruikt (voor zover zichtbaar ingesteld).

> **Let op:** Voor toegang tot het pakketlandschap van andere gemeenten heeft u minimaal de rol *gebruik-raadpleger* nodig.`,
  },

  // ──────────────────────────────────────────────────
  // Aanbod-beheerder (leverancier)
  // ──────────────────────────────────────────────────
  {
    id: "aanbod-overzicht",
    groep: "Leverancier",
    titel: "Pakketaanbod beheren",
    routes: ["/aanbod"],
    routePrefixes: [],
    zoekTermen: [
      "aanbod",
      "leverancier",
      "pakketten beheren",
      "overzicht",
      "mijn pakketten",
    ],
    inhoud: `## Uw pakketaanbod

Op de **Aanbod**-pagina ziet u alle pakketten die u namens uw organisatie hebt geregistreerd.

**Statussen:**
- **Concept** — zichtbaar, maar nog niet publiek actief
- **Actief** — volledig zichtbaar in de publieke catalogus
- **Verouderd** — nog zichtbaar, maar gemarkeerd als verouderd

Klik op een pakket om het te **bewerken**, of gebruik de knop **+ Nieuw pakket** om een pakket toe te voegen.`,
  },

  {
    id: "pakket-registreren",
    groep: "Leverancier",
    titel: "Nieuw pakket registreren",
    routes: ["/aanbod/nieuw"],
    routePrefixes: [],
    zoekTermen: [
      "nieuw pakket",
      "registreren",
      "aanmaken",
      "toevoegen",
      "catalogus",
      "naam",
      "versie",
      "licentie",
    ],
    inhoud: `## Nieuw pakket registreren

1. Ga naar **Aanbod** → **+ Nieuw pakket**
2. Vul het formulier in:
   - **Naam** — officiële productnaam
   - **Versie** — huidig versienummer
   - **Beschrijving** — wat doet het pakket?
   - **Licentievorm** — commercieel / open source / SaaS / anders
   - **Website** — URL naar de productpagina
   - **Cloud-provider** (optioneel) — bijv. Microsoft Azure
3. Klik op **Opslaan**

Het pakket krijgt de status **Concept**. Na controle door de functioneel beheerder wordt het **Actief** en zichtbaar in de catalogus.

> **Tip:** Vul ook de **standaarden** in (DigiD, StUF-BG, etc.) — gemeenten zoeken hier actief op.`,
  },

  {
    id: "pakket-bewerken",
    groep: "Leverancier",
    titel: "Pakket bewerken",
    routes: [],
    routePrefixes: ["/aanbod/"],
    zoekTermen: [
      "bewerken",
      "aanpassen",
      "wijzigen",
      "pakket bijwerken",
      "standaard koppelen",
    ],
    inhoud: `## Pakket bewerken

1. Ga naar **Aanbod**
2. Klik op het pakket
3. Klik op **Bewerken**
4. Pas de gewenste velden aan
5. Klik op **Opslaan**

## Standaarden koppelen

Op de detailpagina van het pakket:
1. Open het tabblad **Standaarden**
2. Klik **+ Standaard toevoegen**
3. Zoek en selecteer de standaard (bijv. DigiD, ZGW API's)
4. Geef aan of de standaard wordt ondersteund
5. Upload desgewenst een **testrapport** (PDF)`,
  },

  // ──────────────────────────────────────────────────
  // Functioneel beheerder
  // ──────────────────────────────────────────────────
  {
    id: "beheer-organisaties",
    groep: "Functioneel beheerder",
    titel: "Organisaties beheren en fiatteren",
    routes: ["/beheer/organisaties"],
    routePrefixes: [],
    zoekTermen: [
      "organisatie",
      "fiatteren",
      "goedkeuren",
      "concept",
      "beheer",
      "gemeente activeren",
      "leverancier activeren",
    ],
    inhoud: `## Organisaties fiatteren

1. Ga naar **Beheer → Organisaties**
2. Filter op **Status: Concept** om aanvragen te zien
3. Klik op een organisatie voor de ingediende gegevens
4. Klik **Fiatteren** om te activeren
5. Of klik **Afwijzen** met een toelichting

Na fiattering ontvangen de gebruikers van de organisatie een bevestigingsmail.

## Organisatie bewerken

Klik op een organisatie → **Bewerken** om naam, type, OIN of website te wijzigen.`,
  },

  {
    id: "beheer-gebruikers",
    groep: "Functioneel beheerder",
    titel: "Gebruikers beheren",
    routes: ["/beheer/gebruikers"],
    routePrefixes: [],
    zoekTermen: [
      "gebruikers",
      "rollen",
      "beheer",
      "gebruiker toevoegen",
      "rol wijzigen",
      "activeren",
      "deactiveren",
    ],
    inhoud: `## Gebruikers beheren

1. Ga naar **Beheer → Gebruikers**
2. Zoek een gebruiker op naam of e-mail
3. Klik op een gebruiker om:
   - De **rol** te wijzigen (bijv. gebruik-raadpleger → gebruik-beheerder)
   - De **status** te wijzigen (actief / inactief)
   - De **organisatiekoppeling** aan te passen

**Rollen in het systeem:**
- **Anoniem / Publiek** — alleen publieke catalogus
- **Gebruik-raadpleger** — landschap inzien
- **Gebruik-beheerder** — volledig beheer eigen landschap
- **Aanbod-beheerder** — pakketten registreren
- **Functioneel beheerder** — alles`,
  },

  {
    id: "beheer-gemma",
    groep: "Functioneel beheerder",
    titel: "GEMMA-model importeren",
    routes: ["/beheer/gemma"],
    routePrefixes: [],
    zoekTermen: [
      "gemma",
      "ameff",
      "archimate",
      "importeren",
      "model",
      "component",
      "architectuur",
    ],
    inhoud: `## GEMMA ArchiMate importeren

1. Ga naar **Beheer → GEMMA**
2. Klik op **AMEFF importeren**
3. Selecteer het AMEFF-bestand (XML van GEMMA Online)
4. Klik op **Importeren starten**

Het systeem rapporteert:
- Nieuwe componenten toegevoegd
- Bestaande componenten bijgewerkt
- Eventuele naamconflicten

> **Belangrijk:** Bestaande koppelingen tussen pakketten en componenten blijven behouden na een import.`,
  },

  // ──────────────────────────────────────────────────
  // Profiel
  // ──────────────────────────────────────────────────
  {
    id: "profiel",
    groep: "Account",
    titel: "Profiel en 2FA-beveiliging",
    routes: ["/profiel"],
    routePrefixes: [],
    zoekTermen: [
      "profiel",
      "wachtwoord wijzigen",
      "2fa",
      "tweefactor",
      "totp",
      "authenticator",
      "beveiliging",
    ],
    inhoud: `## Wachtwoord wijzigen

1. Ga naar **Profiel** (klik op uw naam rechtsboven)
2. Klik op **Wachtwoord wijzigen**
3. Voer uw huidige wachtwoord in
4. Voer tweemaal het nieuwe wachtwoord in
5. Klik op **Opslaan**

## Tweefactorauthenticatie (2FA) instellen

1. Ga naar **Profiel**
2. Klik op **2FA inschakelen**
3. Scan de QR-code met uw authenticator-app
4. Voer de 6-cijferige code ter verificatie in
5. Klik op **Activeren**

> **2FA kwijt?** Neem contact op met uw organisatiebeheerder of met VNG Realisatie (admin@vngrealisatie.nl) om uw 2FA te resetten.`,
  },
];

// ──────────────────────────────────────────────────
// Hulpfuncties
// ──────────────────────────────────────────────────

/**
 * Geeft de meest relevante secties terug voor het opgegeven pad.
 * Exacte matches wegen zwaarder dan prefix-matches.
 */
export function getSectiesVoorRoute(pathname: string): HelpSectie[] {
  const exactMatches = HELP_SECTIES.filter((s) =>
    s.routes.includes(pathname)
  );
  if (exactMatches.length > 0) return exactMatches;

  // Prefix-match: sorteer op langste prefix eerst (meest specifiek)
  const prefixMatches = HELP_SECTIES.filter((s) =>
    s.routePrefixes.some((prefix) => pathname.startsWith(prefix))
  ).sort((a, b) => {
    const aLen = Math.max(...a.routePrefixes.map((p) => p.length));
    const bLen = Math.max(...b.routePrefixes.map((p) => p.length));
    return bLen - aLen;
  });

  return prefixMatches.slice(0, 2);
}

/**
 * Zoek door alle secties op basis van een zoekterm.
 * Geeft resultaten terug gesorteerd op relevantie.
 */
export function zoekInHandleiding(query: string): HelpSectie[] {
  if (!query.trim()) return [];
  const term = query.toLowerCase().trim();

  const scored = HELP_SECTIES.map((s) => {
    let score = 0;
    if (s.titel.toLowerCase().includes(term)) score += 10;
    if (s.groep.toLowerCase().includes(term)) score += 5;
    if (s.zoekTermen.some((t) => t.includes(term) || term.includes(t)))
      score += 8;
    if (s.inhoud.toLowerCase().includes(term)) score += 3;
    return { sectie: s, score };
  });

  return scored
    .filter((r) => r.score > 0)
    .sort((a, b) => b.score - a.score)
    .map((r) => r.sectie);
}

/** Geeft alle unieke groepen terug in volgorde. */
export function getGroepen(): string[] {
  return Array.from(new Set(HELP_SECTIES.map((s) => s.groep)));
}
