const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, PageBreak, LevelFormat,
  ExternalHyperlink, TableOfContents
} = require('docx');
const fs = require('fs');

// ─── Kleuren & stijlen ────────────────────────────────────────────────────────
const VNG_BLAUW   = "154273";   // VNG donkerblauw
const VNG_LICHT   = "D6E4F0";   // lichtblauw achtergrond
const VNG_MIDDEN  = "4A90D9";   // middelste blauw
const GRIJS_LICHT = "F5F5F5";
const GRIJS_RAND  = "CCCCCC";
const GROEN       = "217346";
const ORANJE      = "C55A11";
const ZWART       = "1A1A1A";

const rand = { style: BorderStyle.SINGLE, size: 1, color: GRIJS_RAND };
const celRanden = { top: rand, bottom: rand, left: rand, right: rand };

const celMarge = { top: 100, bottom: 100, left: 160, right: 160 };

// ─── Helpers ──────────────────────────────────────────────────────────────────
function h1(tekst) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 120 },
    children: [new TextRun({ text: tekst, bold: true, font: "Calibri", size: 32, color: VNG_BLAUW })],
  });
}

function h2(tekst) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 80 },
    children: [new TextRun({ text: tekst, bold: true, font: "Calibri", size: 26, color: VNG_BLAUW })],
  });
}

function h3(tekst) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 60 },
    children: [new TextRun({ text: tekst, bold: true, font: "Calibri", size: 22, color: "2E5C8E" })],
  });
}

function alinea(tekst, opties = {}) {
  return new Paragraph({
    spacing: { before: 60, after: 120 },
    children: [new TextRun({ text: tekst, font: "Calibri", size: 22, color: ZWART, ...opties })],
  });
}

function legeRegel() {
  return new Paragraph({ children: [new TextRun("")], spacing: { before: 0, after: 80 } });
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

function stap(nummer, titel, beschrijving) {
  return [
    new Paragraph({
      numbering: { reference: "stappen", level: 0 },
      spacing: { before: 80, after: 40 },
      children: [
        new TextRun({ text: `Stap ${nummer}: `, bold: true, font: "Calibri", size: 22, color: VNG_BLAUW }),
        new TextRun({ text: titel, bold: true, font: "Calibri", size: 22, color: ZWART }),
      ],
    }),
    ...(beschrijving ? [new Paragraph({
      indent: { left: 720 },
      spacing: { before: 0, after: 100 },
      children: [new TextRun({ text: beschrijving, font: "Calibri", size: 22, color: "444444", italics: true })],
    })] : []),
  ];
}

function bullet(tekst, niveau = 0) {
  return new Paragraph({
    numbering: { reference: "bullets", level: niveau },
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text: tekst, font: "Calibri", size: 22, color: ZWART })],
  });
}

function infoKader(regels) {
  const celInhoud = regels.map(r =>
    new Paragraph({
      spacing: { before: 40, after: 40 },
      children: [new TextRun({ text: r, font: "Calibri", size: 20, color: "1A3A5C" })],
    })
  );
  return new Table({
    width: { size: 9026, type: WidthType.DXA },
    columnWidths: [9026],
    rows: [new TableRow({
      children: [new TableCell({
        borders: {
          top:    { style: BorderStyle.SINGLE, size: 4, color: VNG_MIDDEN },
          bottom: { style: BorderStyle.SINGLE, size: 4, color: VNG_MIDDEN },
          left:   { style: BorderStyle.SINGLE, size: 12, color: VNG_MIDDEN },
          right:  { style: BorderStyle.SINGLE, size: 1, color: VNG_LICHT },
        },
        shading: { fill: "EBF3FB", type: ShadingType.CLEAR },
        margins: celMarge,
        width: { size: 9026, type: WidthType.DXA },
        children: celInhoud,
      })],
    })],
  });
}

function credentialsRij(rol, email, wachtwoord, toelichting) {
  return new TableRow({
    children: [
      new TableCell({
        borders: celRanden, margins: celMarge,
        width: { size: 2200, type: WidthType.DXA },
        children: [new Paragraph({ children: [new TextRun({ text: rol, font: "Calibri", size: 20, bold: true, color: VNG_BLAUW })] })],
      }),
      new TableCell({
        borders: celRanden, margins: celMarge,
        width: { size: 2600, type: WidthType.DXA },
        children: [new Paragraph({ children: [new TextRun({ text: email, font: "Courier New", size: 18, color: ZWART })] })],
      }),
      new TableCell({
        borders: celRanden, margins: celMarge,
        width: { size: 1400, type: WidthType.DXA },
        children: [new Paragraph({ children: [new TextRun({ text: wachtwoord, font: "Courier New", size: 18, color: ZWART })] })],
      }),
      new TableCell({
        borders: celRanden, margins: celMarge,
        width: { size: 2826, type: WidthType.DXA },
        children: [new Paragraph({ children: [new TextRun({ text: toelichting, font: "Calibri", size: 18, color: "555555" })] })],
      }),
    ],
  });
}

function tabelKoptekst(kolommen, breedtes) {
  return new TableRow({
    tableHeader: true,
    children: kolommen.map((kol, i) =>
      new TableCell({
        borders: celRanden, margins: celMarge,
        shading: { fill: VNG_BLAUW, type: ShadingType.CLEAR },
        width: { size: breedtes[i], type: WidthType.DXA },
        children: [new Paragraph({ children: [new TextRun({ text: kol, font: "Calibri", size: 20, bold: true, color: "FFFFFF" })] })],
      })
    ),
  });
}

// ─── Document inhoud ──────────────────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 600, hanging: 300 } } } },
          { level: 1, format: LevelFormat.BULLET, text: "\u25E6", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 1000, hanging: 300 } } } },
        ],
      },
      {
        reference: "stappen",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        ],
      },
    ],
  },
  styles: {
    default: {
      document: { run: { font: "Calibri", size: 22 } },
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Calibri", color: VNG_BLAUW },
        paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Calibri", color: VNG_BLAUW },
        paragraph: { spacing: { before: 280, after: 80 }, outlineLevel: 1 },
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: "Calibri", color: "2E5C8E" },
        paragraph: { spacing: { before: 200, after: 60 }, outlineLevel: 2 },
      },
    ],
  },
  sections: [
    // ═══════════════════════════════════════════════════════
    // TITELPAGINA
    // ═══════════════════════════════════════════════════════
    {
      properties: {
        page: {
          size: { width: 11906, height: 16838 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      children: [
        legeRegel(), legeRegel(), legeRegel(), legeRegel(),

        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 0, after: 240 },
          children: [new TextRun({ text: "Softwarecatalogus", font: "Calibri", size: 64, bold: true, color: VNG_BLAUW })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 0, after: 160 },
          children: [new TextRun({ text: "Demonstratiescript", font: "Calibri", size: 40, color: VNG_MIDDEN })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 0, after: 600 },
          border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: VNG_MIDDEN, space: 12 } },
          children: [new TextRun({ text: "Functionele walkthrough van alle rollen en modules", font: "Calibri", size: 24, color: "555555", italics: true })],
        }),

        legeRegel(), legeRegel(), legeRegel(),

        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 0, after: 80 },
          children: [new TextRun({ text: "VNG Realisatie BV", font: "Calibri", size: 28, bold: true, color: ZWART })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 0, after: 80 },
          children: [new TextRun({ text: "Versie 1.0  \u2022  6 maart 2026", font: "Calibri", size: 22, color: "666666" })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 0, after: 80 },
          children: [new TextRun({ text: "Europese aanbesteding TN492936", font: "Calibri", size: 20, color: "888888" })],
        }),

        pageBreak(),
      ],
    },

    // ═══════════════════════════════════════════════════════
    // HOOFDINHOUD
    // ═══════════════════════════════════════════════════════
    {
      properties: {
        page: {
          size: { width: 11906, height: 16838 },
          margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 },
        },
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: VNG_BLAUW, space: 6 } },
              children: [
                new TextRun({ text: "Softwarecatalogus \u2014 Demonstratiescript", font: "Calibri", size: 18, color: "666666" }),
                new TextRun({ text: "\t", font: "Calibri", size: 18 }),
                new TextRun({ text: "VNG Realisatie BV", font: "Calibri", size: 18, color: "888888" }),
              ],
              tabStops: [{ type: "right", position: 9000 }],
            }),
          ],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              border: { top: { style: BorderStyle.SINGLE, size: 4, color: VNG_BLAUW, space: 6 } },
              children: [
                new TextRun({ text: "Vertrouwelijk \u2014 uitsluitend voor intern gebruik", font: "Calibri", size: 16, color: "888888" }),
                new TextRun({ text: "\t", font: "Calibri", size: 16 }),
                new TextRun({ text: "Pagina ", font: "Calibri", size: 16, color: "888888" }),
                new TextRun({ children: [PageNumber.CURRENT], font: "Calibri", size: 16, color: "888888" }),
              ],
              tabStops: [{ type: "right", position: 9000 }],
            }),
          ],
        }),
      },
      children: [

        // ── INHOUDSOPGAVE ──────────────────────────────────
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun({ text: "Inhoudsopgave", font: "Calibri", size: 32, bold: true, color: VNG_BLAUW })],
        }),
        new TableOfContents("Inhoudsopgave", {
          hyperlink: true,
          headingStyleRange: "1-3",
          stylesWithLevels: [
            { styleName: "Heading1", level: 1 },
            { styleName: "Heading2", level: 2 },
            { styleName: "Heading3", level: 3 },
          ],
        }),
        pageBreak(),

        // ── 1. INLEIDING ───────────────────────────────────
        h1("1. Inleiding"),
        alinea("Dit demonstratiescript begeleidt de presentator stap voor stap door alle functionaliteiten van de Softwarecatalogus. Het script is opgedeeld naar gebruikersrol en toont zowel de publieke raadpleegfuncties als de beveiligde beheermodules."),
        legeRegel(),

        h2("1.1 Over de Softwarecatalogus"),
        alinea("De Softwarecatalogus is het centrale platform van VNG Realisatie waarop Nederlandse gemeenten, samenwerkingsverbanden en leveranciers softwarepakketten registreren, vergelijken en raadplegen. Het platform is gebouwd op de GEMMA-referentiearchitectuur en ondersteunt het \u201Cgluren bij de buren\u201D-principe: gemeenten kunnen inzien welke software vergelijkbare gemeenten gebruiken."),
        legeRegel(),

        h2("1.2 Testomgeving"),
        infoKader([
          "\uD83D\uDCBB  Basis-URL: http://localhost",
          "\uD83D\uDD27  Backend API: http://localhost/api/v1/",
          "\uD83D\uDCC5  Versie: 1.0 (MVP)",
          "\u26A0\uFE0F  Let op: dit is een lokale ontwikkelomgeving met voorbeelddata",
        ]),
        legeRegel(),

        h2("1.3 Testaccounts"),
        alinea("Gebruik de volgende accounts tijdens de demonstratie. Alle wachtwoorden zijn identiek."),
        legeRegel(),

        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [2200, 2600, 1400, 2826],
          rows: [
            tabelKoptekst(["Rol", "E-mailadres", "Wachtwoord", "Organisatie / toelichting"], [2200, 2600, 1400, 2826]),
            credentialsRij("Functioneel beheerder", "admin@vngrealisatie.nl", "Welkom01!", "VNG Realisatie \u2014 volledige toegang"),
            credentialsRij("Gebruik-beheerder", "j.jansen@utrecht.nl", "Welkom01!", "Gemeente Utrecht"),
            credentialsRij("Gebruik-beheerder", "m.bakker@amsterdam.nl", "Welkom01!", "Gemeente Amsterdam"),
            credentialsRij("Aanbod-beheerder", "verkoop@centric.eu", "Welkom01!", "Centric (leverancier)"),
            credentialsRij("Aanbod-beheerder", "sales@pinkroccade.nl", "Welkom01!", "PinkRoccade (leverancier)"),
          ],
        }),
        legeRegel(),

        h2("1.4 Rollen en rechten \u2014 overzicht"),
        alinea("Het platform kent de volgende rollen (hi\u00EBrarchisch, van minste naar meeste rechten):"),
        bullet("Publiek / Anoniem \u2014 inzien publieke catalogusinformatie"),
        bullet("Aanbod-raadpleger \u2014 uitgebreid raadplegen van aanbod en gebruik"),
        bullet("Gebruik-raadpleger \u2014 inzien pakketlandschappen van andere gemeenten"),
        bullet("Aanbod-beheerder \u2014 pakketten registreren namens leverancier"),
        bullet("Gebruik-beheerder \u2014 eigen pakketlandschap beheren (gemeente)"),
        bullet("Functioneel beheerder \u2014 volledige beheertoegang (VNG Realisatie)"),

        pageBreak(),

        // ── DEEL A: PUBLIEK RAADPLEGEN ─────────────────────
        h1("2. Deel A \u2014 Publiek raadplegen (anoniem)"),
        alinea("Dit deel toont alle functies die beschikbaar zijn zonder in te loggen. Elke burger, gemeente of leverancier kan deze informatie raadplegen."),
        legeRegel(),

        h2("2.1 Homepage"),
        infoKader(["\uD83D\uDD17  Navigeer naar: http://localhost"]),
        legeRegel(),
        ...stap(1, "Open de homepage", "De homepage toont de kernfuncties van het platform: catalogus, \u201Cgluren bij de buren\u201D en GEMMA-architectuur."),
        ...stap(2, "Toon de navigatiebalk", "Bovenin staan de hoofdsecties: Pakketten, Organisaties, Standaarden. Rechts de knop \u201CInloggen\u201D."),
        ...stap(3, "Klik op \u201CBekijk de catalogus\u201D", "Directe link naar de pakkettenlijst."),
        legeRegel(),

        h2("2.2 Pakketcatalogus browsen"),
        infoKader(["\uD83D\uDD17  Navigeer naar: http://localhost/pakketten"]),
        legeRegel(),
        alinea("De catalogus toont alle geregistreerde softwarepakketten van Nederlandse leveranciers."),
        ...stap(1, "Bekijk het overzicht", "29 pakketten worden getoond met naam, leverancier, licentievorm en status."),
        ...stap(2, "Doorblader de filters in de zijbalk", "Filters op: licentievorm (Commercieel, Open Source, SaaS, Anders), cloud provider, status."),
        ...stap(3, "Filter op \u201CSaaS\u201D", "Klik op \u201CSaaS\u201D in het filter. De lijst wordt direct gefilterd zonder pagina-herlaad."),
        ...stap(4, "Sorteer op naam", "Gebruik het sorteeronderdeel boven de lijst om op naam A-Z te sorteren."),
        ...stap(5, "Reset alle filters", "Klik op \u201CReset filters\u201D om de volledige lijst opnieuw te tonen."),
        legeRegel(),

        h2("2.3 Pakket detailpagina"),
        infoKader(["\uD83D\uDD17  Klik op een pakket, bijv. \u201CSuite4Gemeenten\u201D"]),
        legeRegel(),
        ...stap(1, "Open Suite4Gemeenten", "De detailpagina toont alle informatie over het pakket."),
        ...stap(2, "Bekijk de gegevensblokken", "Per blok: beschrijving, licentievorm (SaaS), cloud provider (Microsoft Azure), aantal gebruikende gemeenten (15)."),
        ...stap(3, "Bekijk \u201COndersteunde standaarden\u201D", "Toont CMIS, DigiD, HTTPS/HSTS, SAML, StUF-BG, StUF-ZKN, TLS, WCAG, ZGW API\u2019s."),
        ...stap(4, "Bekijk \u201CGEMMA componenten\u201D", "Pakketten zijn gekoppeld aan GEMMA-referentiecomponenten: Klantcontactsysteem, Midoffice, Zaakregistratieservice etc."),
        ...stap(5, "Bekijk \u201CGebruikt door\u201D", "Lijst van gemeenten die dit pakket in gebruik hebben (15 stuks)."),
        ...stap(6, "Navigeer terug", "Gebruik de \u201C\u2190 Terug naar pakketten\u201D-link bovenaan."),
        legeRegel(),

        h2("2.4 Organisatieoverzicht"),
        infoKader(["\uD83D\uDD17  Navigeer naar: http://localhost/organisaties"]),
        legeRegel(),
        ...stap(1, "Bekijk de filteropties", "Tabs voor: Alle typen | Gemeenten | Leveranciers | Samenwerkingsverbanden."),
        ...stap(2, "Filter op \u201CLeveranciers\u201D", "Toont 17 leveranciers zoals Centric, PinkRoccade, Atos, BCT."),
        ...stap(3, "Open de detailpagina van Centric", "Toont naam, type, beschrijving, website, contactpersonen."),
        ...stap(4, "Filter op \u201CGemeenten\u201D", "30 gemeenten geregistreerd, met links naar hun pakketlandschappen."),
        legeRegel(),

        h2("2.5 Standaarden"),
        infoKader(["\uD83D\uDD17  Navigeer naar: http://localhost/standaarden"]),
        legeRegel(),
        ...stap(1, "Bekijk het standaardenoverzicht", "18 standaarden van Forum Standaardisatie, geordend met type (Verplicht / Aanbevolen)."),
        ...stap(2, "Bekijk voorbeelden", "DigiD (Verplicht), SAML (Verplicht), ZGW API\u2019s (Verplicht), ArchiMate (Aanbevolen)."),
        ...stap(3, "Klik \u201CForum Standaardisatie \u2192\u201D", "Externe link naar de officiële standaarddocumentatie."),

        pageBreak(),

        // ── DEEL B: GEMEENTE GEBRUIKER ─────────────────────
        h1("3. Deel B \u2014 Gemeente: Gebruik-beheerder"),
        alinea("Dit deel toont de functies voor een gemeente-medewerker die het eigen pakketlandschap beheert. We gebruiken het account van Jan Jansen (Gemeente Utrecht)."),
        legeRegel(),
        infoKader([
          "\uD83D\uDC64  Account: j.jansen@utrecht.nl  |  Wachtwoord: Welkom01!",
          "\uD83C\uDFDB\uFE0F  Organisatie: Gemeente Utrecht",
          "\uD83D\uDD11  Rol: Gebruik-beheerder",
        ]),
        legeRegel(),

        h2("3.1 Inloggen"),
        infoKader(["\uD83D\uDD17  Navigeer naar: http://localhost/login"]),
        legeRegel(),
        ...stap(1, "Vul het e-mailadres in", "Typ: j.jansen@utrecht.nl"),
        ...stap(2, "Vul het wachtwoord in", "Typ: Welkom01!"),
        ...stap(3, "Klik op \u201CInloggen\u201D", "Na succesvolle authenticatie wordt u doorgestuurd naar \u201CMijn pakketlandschap\u201D."),
        ...stap(4, "Bekijk de navigatiebalk", "Bovenin verschijnt de naam \u201CJan Jansen\u201D in plaats van de \u201CInloggen\u201D-knop."),
        legeRegel(),

        h2("3.2 Mijn pakketlandschap"),
        infoKader(["\uD83D\uDD17  Navigeer naar: http://localhost/mijn-landschap"]),
        legeRegel(),
        ...stap(1, "Bekijk de zijbalk", "Toont gebruikersnaam (Jan Jansen), rol (Gebruik-beheerder), organisatie (Gemeente Utrecht) en navigatiemenu."),
        ...stap(2, "Bekijk het pakketlandschap", "Overzicht van alle pakketten die Gemeente Utrecht in gebruik heeft. Elke rij toont: pakketnaam, startdatum, status (In gebruik / Gepland)."),
        ...stap(3, "Bespreek het \u201Cgluren bij de buren\u201D-principe", "Via de publieke catalogus kan elke gemeente zien welke pakketten Gemeente Utrecht gebruikt \u2014 en omgekeerd."),
        legeRegel(),

        h2("3.3 Profiel bekijken"),
        infoKader(["\uD83D\uDD17  Klik op \u201CMijn profiel\u201D in de zijbalk"]),
        legeRegel(),
        ...stap(1, "Bekijk de profielinformatie", "Naam, e-mailadres, organisatie, rol en 2FA-status (uitgeschakeld in testomgeving)."),
        ...stap(2, "Toon 2FA-functionaliteit", "In productie kan de gebruiker hier TOTP-verificatie instellen via een authenticator-app."),
        legeRegel(),

        h2("3.4 Uitloggen"),
        ...stap(1, "Klik op \u201CUitloggen\u201D in de zijbalk", "De sessie wordt be\u00EBindigd en tokens worden gewist."),
        ...stap(2, "Bevestig redirect", "De gebruiker wordt teruggeleid naar de loginpagina."),

        pageBreak(),

        // ── DEEL C: LEVERANCIER ────────────────────────────
        h1("4. Deel C \u2014 Leverancier: Aanbod-beheerder"),
        alinea("Leveranciers kunnen hun softwarepakketten registreren en beheren. We gebruiken het account van de accountmanager bij Centric."),
        legeRegel(),
        infoKader([
          "\uD83D\uDC64  Account: verkoop@centric.eu  |  Wachtwoord: Welkom01!",
          "\uD83C\uDFE2  Organisatie: Centric",
          "\uD83D\uDD11  Rol: Aanbod-beheerder",
        ]),
        legeRegel(),

        h2("4.1 Inloggen als leverancier"),
        ...stap(1, "Log in met het Centric-account", "Navigeer naar /login en gebruik verkoop@centric.eu / Welkom01!"),
        ...stap(2, "Bekijk het dashboard", "De zijbalk toont \u201CPakketaanbod beheren\u201D als primaire actie."),
        legeRegel(),

        h2("4.2 Pakketaanbod beheren"),
        infoKader(["\uD83D\uDD17  Navigeer naar: http://localhost/aanbod"]),
        legeRegel(),
        ...stap(1, "Bekijk de beheerpagina", "Toont de optie om nieuwe pakketten te registreren."),
        ...stap(2, "Bespreek het registratieproces", "Een nieuw pakket krijgt automatisch concept-status. De functioneel beheerder van VNG Realisatie moet het fiatteren voordat het publiek zichtbaar wordt."),
        ...stap(3, "Bekijk bestaande pakketten in de catalogus", "Via /pakketten zijn alle actieve Centric-pakketten zichtbaar: Suite4Gemeenten, Centric Belastingen, Key2Burgerzaken etc."),
        legeRegel(),

        h2("4.3 Concept-status patroon"),
        alinea("Een belangrijk principe: alles wat aangemaakt wordt door een niet-eigenaar krijgt concept-status."),
        bullet("Leverancier registreert pakket \u2192 concept, wacht op fiattering"),
        bullet("Gemeente registreert een pakket namens ontbrekende leverancier \u2192 ook concept"),
        bullet("Functioneel beheerder van VNG Realisatie fiatteert \u2192 pakket wordt actief"),

        pageBreak(),

        // ── DEEL D: FUNCTIONEEL BEHEERDER ─────────────────
        h1("5. Deel D \u2014 VNG Realisatie: Functioneel beheerder"),
        alinea("De functioneel beheerder heeft volledige toegang en beheert het platform: organisaties fiatteren, GEMMA-data importeren en het platform configureren."),
        legeRegel(),
        infoKader([
          "\uD83D\uDC64  Account: admin@vngrealisatie.nl  |  Wachtwoord: Welkom01!",
          "\uD83C\uDFDB\uFE0F  Organisatie: VNG Realisatie BV",
          "\uD83D\uDD11  Rol: Functioneel beheerder \u2014 volledige toegang",
        ]),
        legeRegel(),

        h2("5.1 Inloggen als beheerder"),
        ...stap(1, "Log in met het VNG-account", "Navigeer naar /login en gebruik admin@vngrealisatie.nl / Welkom01!"),
        ...stap(2, "Bekijk het uitgebreide dashboard", "De zijbalk toont extra menu-items: Organisatiebeheer en GEMMA beheer."),
        legeRegel(),

        h2("5.2 Organisatiebeheer"),
        infoKader(["\uD83D\uDD17  Navigeer naar: http://localhost/beheer/organisaties"]),
        legeRegel(),
        ...stap(1, "Bekijk de beheerpagina", "Toont organisaties die wachten op fiattering (concept-status)."),
        ...stap(2, "Bekijk de wachtende organisatie", "\u201CNieuwe Software BV\u201D is aangemeld als nieuwe leverancier en wacht op goedkeuring."),
        ...stap(3, "Klik op \u201CFiatteren\u201D", "De organisatie krijgt status \u201CActief\u201D en de aanmelder ontvangt een welkomstmail."),
        ...stap(4, "Bespreek verdere mogelijkheden", "Functioneel beheerder kan ook organisaties samenvoegen (bijv. bij gemeentelijke herindeling)."),
        legeRegel(),

        h2("5.3 GEMMA beheer \u2014 componentenoverzicht"),
        infoKader(["\uD83D\uDD17  Navigeer naar: http://localhost/beheer/gemma"]),
        legeRegel(),
        ...stap(1, "Bekijk de componentenlijst", "25 GEMMA-componenten zijn geregistreerd: applicatiecomponenten en applicatieservices."),
        ...stap(2, "Bekijk de tabel", "Per component: naam, type (applicatiecomponent / applicatieservice), ArchiMate-ID (bijv. GEMMA-AC-002 voor Burgerzakensysteem)."),
        ...stap(3, "Bespreek de koppeling", "Elk pakket in de catalogus kan worden gekoppeld aan \u00E9\u00E9n of meerdere GEMMA-componenten. Dit maakt architectuurvisualisatie mogelijk."),
        legeRegel(),

        h2("5.4 GEMMA beheer \u2014 AMEFF importeren"),
        alinea("Het GEMMA-referentiemodel wordt beheerd in ArchiMate en gepubliceerd als AMEFF-bestand. De functioneel beheerder kan updates importeren."),
        legeRegel(),
        ...stap(1, "Klik op \u201CAMEFF XML-bestand\u201D", "Uploadknop voor het ArchiMate Exchange Model File Format (.xml)."),
        ...stap(2, "Selecteer een AMEFF-bestand", "Het systeem parseert ApplicationComponent- en ApplicationService-elementen."),
        ...stap(3, "Klik op \u201CImporteren\u201D", "Componenten worden gesynchroniseerd. Bestaande koppelingen pakket\u2194component blijven behouden."),
        ...stap(4, "Bespreek de export", "Gebruik-beheerders kunnen hun pakketlandschap exporteren als AMEFF. Dit bestand is importeerbaar in Archi, Sparx EA en BiZZdesign."),
        legeRegel(),

        h2("5.5 Uitloggen"),
        ...stap(1, "Klik op \u201CUitloggen\u201D in de zijbalk", "Sessie wordt volledig beeindigd."),

        pageBreak(),

        // ── DEEL E: API ────────────────────────────────────
        h1("6. Deel E \u2014 API demonstratie"),
        alinea("De Softwarecatalogus biedt een publieke en beveiligde REST API conform de NL API Strategie. De API is API-first ontworpen en gedocumenteerd met OpenAPI 3.x."),
        legeRegel(),

        h2("6.1 Publieke API (geen authenticatie vereist)"),
        infoKader(["\uD83D\uDD17  Swagger UI: http://localhost/api/schema/swagger-ui/"]),
        legeRegel(),

        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [3200, 1200, 4626],
          rows: [
            tabelKoptekst(["Endpoint", "Methode", "Beschrijving"], [3200, 1200, 4626]),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3200, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "/api/v1/pakketten/", font: "Courier New", size: 18 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 1200, type: WidthType.DXA }, shading: { fill: "EBF7EE", type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "GET", font: "Courier New", size: 18, bold: true, color: GROEN })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 4626, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Lijst van alle pakketten (zoek/filter)", font: "Calibri", size: 20 })] })] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3200, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "/api/v1/pakketten/{id}/", font: "Courier New", size: 18 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 1200, type: WidthType.DXA }, shading: { fill: "EBF7EE", type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "GET", font: "Courier New", size: 18, bold: true, color: GROEN })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 4626, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Detail van een pakket", font: "Calibri", size: 20 })] })] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3200, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "/api/v1/organisaties/", font: "Courier New", size: 18 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 1200, type: WidthType.DXA }, shading: { fill: "EBF7EE", type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "GET", font: "Courier New", size: 18, bold: true, color: GROEN })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 4626, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Leveranciers, gemeenten en samenwerkingsverbanden", font: "Calibri", size: 20 })] })] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3200, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "/api/v1/standaarden/", font: "Courier New", size: 18 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 1200, type: WidthType.DXA }, shading: { fill: "EBF7EE", type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "GET", font: "Courier New", size: 18, bold: true, color: GROEN })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 4626, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Forum Standaardisatie standaardenlijst", font: "Calibri", size: 20 })] })] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3200, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "/api/v1/gemma/componenten/", font: "Courier New", size: 18 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 1200, type: WidthType.DXA }, shading: { fill: "EBF7EE", type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "GET", font: "Courier New", size: 18, bold: true, color: GROEN })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 4626, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "GEMMA referentiecomponenten", font: "Calibri", size: 20 })] })] }),
            ]}),
          ],
        }),
        legeRegel(),

        h2("6.2 Beveiligde API (JWT authenticatie vereist)"),

        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [3200, 1200, 4626],
          rows: [
            tabelKoptekst(["Endpoint", "Methode", "Beschrijving"], [3200, 1200, 4626]),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3200, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "/api/v1/auth/login/", font: "Courier New", size: 18 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 1200, type: WidthType.DXA }, shading: { fill: "FFF3E0", type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "POST", font: "Courier New", size: 18, bold: true, color: ORANJE })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 4626, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Inloggen \u2192 JWT access + refresh token", font: "Calibri", size: 20 })] })] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3200, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "/api/v1/mijn-organisatie/pakketoverzicht/", font: "Courier New", size: 18 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 1200, type: WidthType.DXA }, shading: { fill: "EBF7EE", type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "GET", font: "Courier New", size: 18, bold: true, color: GROEN })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 4626, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Eigen pakketlandschap (gemeente)", font: "Calibri", size: 20 })] })] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3200, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "/api/v1/mijn-organisatie/pakketoverzicht/", font: "Courier New", size: 18 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 1200, type: WidthType.DXA }, shading: { fill: "FFF3E0", type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "POST", font: "Courier New", size: 18, bold: true, color: ORANJE })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 4626, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Pakket toevoegen aan landschap", font: "Calibri", size: 20 })] })] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3200, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "/api/v1/export/pakketoverzicht.xlsx", font: "Courier New", size: 18 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 1200, type: WidthType.DXA }, shading: { fill: "EBF7EE", type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "GET", font: "Courier New", size: 18, bold: true, color: GROEN })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 4626, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Export pakketlandschap als Excel", font: "Calibri", size: 20 })] })] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3200, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "/api/v1/admin/gemma/importeer/", font: "Courier New", size: 18 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 1200, type: WidthType.DXA }, shading: { fill: "FFF3E0", type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "POST", font: "Courier New", size: 18, bold: true, color: ORANJE })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 4626, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "AMEFF importeren (admin only)", font: "Calibri", size: 20 })] })] }),
            ]}),
          ],
        }),
        legeRegel(),

        h2("6.3 Live API-aanroep demonstreren"),
        alinea("Open de browser en navigeer naar de volgende URL om de publieke API live te zien:"),
        legeRegel(),
        infoKader([
          "http://localhost/api/v1/pakketten/?licentievorm=saas",
          "  \u21AA Toont alle SaaS-pakketten als JSON",
          "",
          "http://localhost/api/v1/pakketten/?search=suite",
          "  \u21AA Zoekfunctie op pakketnaam",
          "",
          "http://localhost/api/schema/swagger-ui/",
          "  \u21AA Interactieve API-documentatie (OpenAPI 3.x)",
        ]),

        pageBreak(),

        // ── APPENDIX ───────────────────────────────────────
        h1("Bijlage A \u2014 Testdata overzicht"),
        alinea("De volgende data is ingevoerd via het \u2018seed_data\u2019-commando als realistische voorbeelddata voor de demonstratie."),
        legeRegel(),

        h2("Organisaties"),
        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [3000, 2013, 4013],
          rows: [
            tabelKoptekst(["Type", "Aantal", "Voorbeelden"], [3000, 2013, 4013]),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3000, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Gemeenten", font: "Calibri", size: 20 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 2013, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "30", font: "Calibri", size: 20, bold: true })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 4013, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Amsterdam, Rotterdam, Utrecht, Den Haag, ...", font: "Calibri", size: 20 })] })] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3000, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Leveranciers", font: "Calibri", size: 20 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 2013, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "17", font: "Calibri", size: 20, bold: true })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 4013, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Centric, PinkRoccade, Atos, BCT, Decos, ...", font: "Calibri", size: 20 })] })] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3000, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Samenwerkingsverbanden", font: "Calibri", size: 20 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 2013, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "5", font: "Calibri", size: 20, bold: true })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 4013, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Dimpact, Drechtsteden, BSOB, ...", font: "Calibri", size: 20 })] })] }),
            ]}),
          ],
        }),
        legeRegel(),

        h2("Softwarecatalogus"),
        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [3600, 1800, 3626],
          rows: [
            tabelKoptekst(["Categorie", "Aantal", "Toelichting"], [3600, 1800, 3626]),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3600, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Pakketten (actief)", font: "Calibri", size: 20 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 1800, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "28", font: "Calibri", size: 20, bold: true })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3626, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Zaaksystemen, burgerzaken, financieel, etc.", font: "Calibri", size: 20 })] })] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3600, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Pakketten (concept / verouderd)", font: "Calibri", size: 20 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 1800, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "2", font: "Calibri", size: 20, bold: true })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3626, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Ter illustratie van het concept-statuspatroon", font: "Calibri", size: 20 })] })] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3600, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Pakketgebruik-registraties", font: "Calibri", size: 20 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 1800, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "280", font: "Calibri", size: 20, bold: true })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3626, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Gemeenten x pakketten (gebruik-registraties)", font: "Calibri", size: 20 })] })] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3600, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "GEMMA-componenten", font: "Calibri", size: 20 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 1800, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "25", font: "Calibri", size: 20, bold: true })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3626, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "ArchiMate applicatiecomponenten en -services", font: "Calibri", size: 20 })] })] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3600, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Forum Standaardisatie standaarden", font: "Calibri", size: 20 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 1800, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "18", font: "Calibri", size: 20, bold: true })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3626, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Verplicht en aanbevolen standaarden", font: "Calibri", size: 20 })] })] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3600, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Gebruikers", font: "Calibri", size: 20 })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 1800, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "25", font: "Calibri", size: 20, bold: true })] })] }),
              new TableCell({ borders: celRanden, margins: celMarge, width: { size: 3626, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Meerdere rollen verdeeld over organisaties", font: "Calibri", size: 20 })] })] }),
            ]}),
          ],
        }),
        legeRegel(),

        h2("Bijlage B \u2014 Aandachtspunten voor de demonstratie"),
        legeRegel(),
        bullet("Ververs de pagina niet midden in de demonstratie \u2014 bij verversing zonder token verdwijnt de ingelogde sessie"),
        bullet("Gebruik bij voorkeur Chrome of Edge voor de beste ervaring"),
        bullet("TOTP (2FA) is uitgeschakeld in de testomgeving \u2014 in productie is dit verplicht voor alle beheeraccounts"),
        bullet("De zoekfunctie werkt op naam, beschrijving en GEMMA-component via Meilisearch"),
        bullet("De API-documentatie is beschikbaar via /api/schema/swagger-ui/ en /api/schema/redoc/"),
        bullet("Docker moet draaien voor de demonstratie: docker compose up -d"),
        legeRegel(),

        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 480 },
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: VNG_BLAUW, space: 8 } },
          children: [new TextRun({ text: "Einde demonstratiescript  \u2014  Softwarecatalogus v1.0  \u2014  VNG Realisatie BV", font: "Calibri", size: 18, color: "888888", italics: true })],
        }),
      ],
    },
  ],
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('/output/Demonstratiescript_Softwarecatalogus.docx', buffer);
  console.log('OK: Demonstratiescript_Softwarecatalogus.docx aangemaakt');
});
