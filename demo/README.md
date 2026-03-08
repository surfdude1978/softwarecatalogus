# Softwarecatalogus — Geautomatiseerde Demo-opname

Playwright-gebaseerde demo-runner die de Softwarecatalogus opneemt als **vier persona-gerichte video's**.

## Vereisten

| Tool | Versie | Doel |
|------|--------|------|
| Node.js | ≥ 18 | Runtime |
| npm | ≥ 9 | Pakketbeheer |
| ffmpeg | any | Clips samenvoegen tot mp4 |
| Playwright Chromium | via npm | Browserbediening |
| Softwarecatalogus | draaiend op `http://localhost` | De te demonstreren app |

## Installatie

```bash
cd demo/
npm install
npm run install-browsers
```

## Gebruik

### 1. Éénmalig: auth-states aanmaken

```bash
npm run setup-auth
```

### 2. Vier persona-video's opnemen

Elke video is onafhankelijk en kan apart worden opgenomen:

```bash
npm run publiek       # swc-demo-publiek.mp4     — publieke catalogus
npm run gemeente      # swc-demo-gemeente.mp4    — gebruik-beheerder
npm run leverancier   # swc-demo-leverancier.mp4 — aanbod-beheerder
npm run vng           # swc-demo-vng.mp4         — functioneel beheerder + API
```

Of alle vier in één keer:
```bash
npm run all-suites
```

### 3. Eén scène testen

```bash
npm run scene -- 01        # 01-homepage
npm run scene -- 07        # 07-mijn-landschap
npm run scene -- 13        # 13-gemma-beheer
```

### 4. Clips samenvoegen zonder opnieuw op te nemen

```bash
npm run merge                          # alle clips in output/clips/
npm run merge -- --suite gemeente      # alleen de gemeente-clips
```

### 5. Overzichten

```bash
npm run list            # alle 16 scènes
npm run list-suites     # de 4 suites met hun scènes
```

## Suites (persona-video's)

| Suite | Commando | Scènes | Output |
|-------|----------|--------|--------|
| **Publieke catalogus** | `npm run publiek` | 01–05 | `swc-demo-publiek.mp4` |
| **Gemeente gebruik-beheerder** | `npm run gemeente` | 06–08 | `swc-demo-gemeente.mp4` |
| **Leverancier aanbod-beheerder** | `npm run leverancier` | 09–10 | `swc-demo-leverancier.mp4` |
| **VNG Realisatie beheerder + API** | `npm run vng` | 11–16 | `swc-demo-vng.mp4` |

## Scèneoverzicht

| # | Naam | Inhoud | Suite |
|---|------|--------|-------|
| 01 | homepage | Hero, feature-blokken | publiek |
| 02 | pakketten | Zoeken, filteren (SaaS), sorteren, reset | publiek |
| 03 | pakketdetail | Suite4Gemeenten: metadata, standaarden, GEMMA | publiek |
| 04 | organisaties | Overzicht + organisatiedetail | publiek |
| 05 | standaarden | Verplicht/aanbevolen, Forum Standaardisatie-links | publiek |
| 06 | login-gemeente | Inloggen als Jan Jansen (Gemeente Utrecht) | gemeente |
| 07 | mijn-landschap | Pakketoverzicht gemeente | gemeente |
| 08 | logout-gemeente | Uitloggen | gemeente |
| 09 | login-leverancier | Inloggen als Centric | leverancier |
| 10 | aanbod-beheren | Pakketbeheer, concept-status patroon | leverancier |
| 11 | login-admin | Inloggen als Lisa de Vries (VNG Realisatie) | vng |
| 12 | organisatiebeheer | Fiattering NieuweSoftware BV | vng |
| 13 | gemma-beheer | 25 GEMMA-componenten, AMEFF-importformulier | vng |
| 14 | ameff-import | Demo AMEFF XML uploaden | vng |
| 15 | api-swagger | Swagger UI, endpoints doorlopen | vng |
| 16 | api-live | Live JSON-responses in browser | vng |

## Omgevingsvariabelen

| Variabele | Default | Beschrijving |
|-----------|---------|--------------|
| `DEMO_BASE_URL` | `http://localhost` | URL van de app (Docker: `http://host.docker.internal`) |
| `DEMO_SLOW` | `1.0` | Timing-factor: `1.5` = 50% langzamer, `0.8` = 20% sneller |

Voorbeeld:
```bash
DEMO_SLOW=1.3 npm run gemeente
```

## Visuele elementen in de video

- **Cursor**: rode stip die elke muisbeweging volgt (automatisch ingeladen)
- **Stap-annotatie**: blauw kader onderin het midden (altijd volledig in beeld)
- **Hoofdstuktitel**: full-screen overlay bij start van elke suite
- **Highlight**: gekleurde rand om aandacht te vestigen op een element

## Projectstructuur

```
demo/
├── run-demo.ts          # Orkestrator + suites + CLI
├── setup-auth.ts        # Auth-states aanmaken
├── helpers/
│   ├── config.ts        # URL, viewport, accounts, OUTPUT_DIR
│   ├── timing.ts        # short/medium/long, waitForStable, DEMO_SLOW
│   ├── overlay.ts       # Annotaties, cursor-tracker, highlights
│   └── auth.ts          # loginApi, logout, selectOption, fillReact
├── scenes/              # 16 scènes
└── output/
    ├── clips/           # Losse .webm clips per scène
    ├── swc-demo-publiek.mp4
    ├── swc-demo-gemeente.mp4
    ├── swc-demo-leverancier.mp4
    └── swc-demo-vng.mp4
```

## Testaccounts

| Rol | Email | Wachtwoord |
|-----|-------|-----------|
| Gebruik-beheerder (gemeente) | j.jansen@utrecht.nl | Welkom01! |
| Aanbod-beheerder (leverancier) | verkoop@centric.eu | Welkom01! |
| Functioneel beheerder (VNG) | admin@vngrealisatie.nl | Welkom01! |
