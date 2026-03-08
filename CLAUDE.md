# Softwarecatalogus — Instructies voor Claude Code

## Projectoverzicht

De **Softwarecatalogus** is een centraal platform voor Nederlandse gemeenten, samenwerkingsverbanden en leveranciers om software-applicaties te registreren, vergelijken en raadplegen. Het platform maakt deel uit van de VNG Realisatie dienstverlening en vervangt de bestaande softwarecatalogus.nl.

### Opdrachtgever
**VNG Realisatie BV** — ondersteunt alle Nederlandse gemeenten bij gezamenlijk ICT-gebruik.

### Kernfunctie
Een digitale bibliotheek en kennisdelingsplatform voor ICT-software-behoeften van gemeenten, geïntegreerd met de GEMMA-referentiearchitectuur (ArchiMate).

---

## Tech Stack (verplicht/aanbevolen)

### Backend
- **Python 3.12+** met **Django 5.x** + **Django REST Framework**
- **PostgreSQL 16** als primaire database
- **Meilisearch** voor full-text zoekfunctionaliteit
- **Celery** + **Redis** voor async taken (import/export, migratie)
- **drf-spectacular** voor OpenAPI 3.x spec-generatie (API-first)
- **django-allauth** + **django-otp** voor 2FA authenticatie (TOTP)
- **django-guardian** voor object-level permissions

### Frontend
- **Next.js 14+** (App Router) met **TypeScript**
- **Tailwind CSS** voor styling
- **shadcn/ui** voor componenten
- **React Query (TanStack Query)** voor data fetching
- **Zustand** voor state management
- Toegankelijkheid: WCAG 2.1 AA (digitoegankelijk.nl standaard)

### Infrastructuur
- **Docker** + **docker-compose** voor lokale ontwikkeling
- **Kubernetes**-compatibel (Haven-platform)
- **OTAP**: Ontwikkel, Test, Acceptatie, Productie omgevingen
- **Matomo** voor privacyvriendelijke webstatistieken
- **Nginx** als reverse proxy

### Code & Licentie
- Broncode: **EUPL-1.2 licentie** (verplicht)
- Git repository: GitHub of GitLab
- CI/CD met geautomatiseerde tests en deployments

---

## Datamodel

### Kernentiteiten (gebaseerd op Informatiemodel Voorzieningencatalogus)

```
Organisatie
  - id (UUID)
  - naam
  - type: ['gemeente', 'samenwerkingsverband', 'leverancier', 'overig']
  - status: ['concept', 'actief', 'inactief']
  - oin (Organisatie Identificatienummer)
  - bevoegd_gezag_code
  - contactpersonen[]
  - geregistreerd_door (User, voor concept-status)
  - aangemaakt_op, gewijzigd_op

Pakket (SoftwareVoorziening)
  - id (UUID)
  - naam
  - versie
  - status: ['concept', 'actief', 'verouderd', 'ingetrokken']
  - beschrijving
  - leverancier (FK Organisatie)
  - licentievorm: ['commercieel', 'open_source', 'saas', 'anders']
  - open_source_licentie (bijv. EUPL, MIT, GPL)
  - contactpersoon
  - website_url
  - documentatie_url
  - cloud_provider (optioneel: Microsoft Azure, AWS, etc.)
  - geregistreerd_door (User)
  - aangemaakt_op, gewijzigd_op

PakketGebruik (VoorzieningGebruik)
  - id (UUID)
  - pakket (FK Pakket)
  - organisatie (FK Organisatie)
  - status: ['in_gebruik', 'gepland', 'gestopt']
  - start_datum, eind_datum
  - notitie
  - koppelingen[] (naar andere PakketGebruik)
  - aangemaakt_op, gewijzigd_op

Koppeling
  - id (UUID)
  - van_pakket_gebruik (FK PakketGebruik)
  - naar_pakket_gebruik (FK PakketGebruik)
  - type (API, bestand, etc.)
  - beschrijving

Standaard
  - id (UUID)
  - naam
  - type: ['verplicht', 'aanbevolen', 'optioneel']
  - versie
  - forum_standaardisatie_url
  - beschrijving

PakketStandaard (M2M)
  - pakket (FK Pakket)
  - standaard (FK Standaard)
  - ondersteund: bool
  - testrapport_url

GemmaComponent (ReferentieComponent)
  - id (UUID)
  - naam
  - archimate_id
  - type (applicatiecomponent, applicatieservice, etc.)
  - beschrijving
  - gemma_online_url
  - parent (FK GemmaComponent, optional)

PakketGemmaComponent (M2M)
  - pakket (FK Pakket)
  - gemma_component (FK GemmaComponent)

Document
  - id (UUID)
  - pakket (FK Pakket)
  - organisatie (FK Organisatie, optional)
  - type: ['dpia', 'verwerkersovereenkomst', 'pentest', 'overig']
  - naam
  - bestand (file upload)
  - status: ['concept', 'gepubliceerd']
  - gedeeld_met: ['publiek', 'gemeenten', 'prive']
  - aangemaakt_op

User
  - id (UUID)
  - email
  - naam
  - organisatie (FK Organisatie)
  - rol: zie Gebruikersrollen hieronder
  - totp_enabled: bool
  - aangemaakt_op

Notificatie
  - user (FK User)
  - type
  - bericht
  - gelezen: bool
  - aangemaakt_op
```

---

## Gebruikersrollen en Rechten

### Rollen (hiërarchisch)

| Rol | Beschrijving | Organisatietype |
|-----|--------------|-----------------|
| **Publiek / Anoniem** | Lezen van publieke aanbodinformatie | — |
| **Aanbod-raadpleger** | Inzien aanbod en gebruik van andere gemeenten | Alle |
| **Gebruik-raadpleger** | Inzien eigen én andermans gebruik | Gemeente / SWV |
| **Aanbod-beheerder** | Pakketten registreren en beheren (leverancier) | Leverancier |
| **Gebruik-beheerder** | Eigen pakketlandschap beheren | Gemeente / SWV |
| **IBD-beheerder** | BIO-eisen en beveiligingsstatus monitoren | IBD |
| **GT Inkoop-beheerder** | Collectieve afspraken registreren | VNG GT Inkoop |
| **Functioneel beheerder** | Volledige admin, configuratie, org-beheer | VNG Realisatie |

### Rechtenmatrix (globaal)

- **Publiek**: GET /pakketten, GET /organisaties (basisinfo), GET /standaarden
- **Aanbod-raadpleger**: + zoek/filter op gebruik andere gemeenten
- **Gebruik-raadpleger**: + inzien volledig pakketlandschap gemeenten, "gluren bij de buren"
- **Aanbod-beheerder**: + CRUD eigen pakketten (concept→actief via functioneel beheerder)
- **Gebruik-beheerder**: + CRUD eigen pakketgebruik, exporteren, importeren
- **Functioneel beheerder**: + alles, inclusief organisatiebeheer, fiatteringen, impersonatie

---

## Functionele Eisen (MVP — verplicht te implementeren)

### 1. Aanbod — Raadplegen (EIS)
- Zoeken en filteren pakketten op: naam, leverancier, categorie/GEMMA-component, standaarden (verplicht/aanbevolen), licentievorm, cloud-provider
- Detailpagina pakket: beschrijving, ondersteunde standaarden, GEMMA-componenten, gebruikende gemeenten, gerelateerde pakketten, documenten
- Autocompletion in zoekbalk
- Sorteren op naam, populariteit, recent bijgewerkt

### 2. Aanbod — Registreren pakketten (EIS)
- Aanbod-beheerder registreert pakketten namens leverancier
- Pakket krijgt **concept-status** bij aanmaken door gebruik-beheerder (niet-leverancier); concept-status altijd zichtbaar
- Contactpersoon per pakket instellen
- Standaarden koppelen + testrapport uploaden
- Licentievorm registreren (incl. open source)
- Gebruik-beheerder kan concept-pakket aanmaken voor ontbrekende leverancier

### 3. Gebruik — Raadplegen (EIS)
- Pakketoverzicht filteren op meerdere eigenschappen
- "Gluren bij de buren": pakketlandschap andere gemeente bekijken
- Inzien welke gemeenten een pakket gebruiken
- Inzien vergelijkbare pakketten bij pakketdetail
- Zoeken en filteren in alle gebruikte pakketten (cross-gemeente)

### 4. Gebruik — Registreren (EIS)
- Gebruik-beheerder selecteert pakketten uit catalogus en voegt toe aan eigen overzicht
- Koppelingen registreren tussen pakketten (welk pakket koppelt met welk)
- Pakketten archiveren/verwijderen uit eigen overzicht

### 5. GEMMA Referentiearchitectuur (EIS)
- GEMMA ArchiMate-model importeren (AMEFF-formaat) door functioneel beheerder
- Pakketten koppelen aan GEMMA-componenten (referentiecomponenten, applicatieservices)
- Architectuurkaart tonen: visuele weergave van pakketlandschap op GEMMA-kaart
- Export van pakketoverzicht als AMEFF-bestand (ArchiMate Exchange)
- Glossary: GEMMA-begrippen uitleggen met doorverwijzing naar GEMMA Online

### 6. Exporteren (EIS)
- Export van pakketoverzicht en aanbodinformatie als:
  - CSV / Excel (.xlsx)
  - AMEFF (ArchiMate Exchange Model File Format)
  - JSON (API-formaat)

### 7. Organisatiebeheer (EIS)
- Zelfregistratie leveranciers (concept → fiattering door functioneel beheerder)
- Gebruik-beheerder kan ontbrekende aanbieder registreren (concept)
- Functioneel beheerder: organisaties samenvoegen (bij herindeling/overname)
- Meerdere gebruikers per organisatie, beheerd door aanbod/gebruik-beheerder

### 8. Gebruikers & Toegang (EIS)
- Registratie en login met **2FA (TOTP)**
- Zelfregistratie gebruikers bij bestaande organisaties (fiattering door org-beheerder)
- Wachtwoord vergeten / reset via e-mail (DKIM + DMARC)
- Gebruikersrollen per organisatie beheren
- Impersonatie door functioneel beheerder

### 9. Content & Configuratie (EIS)
- CMS-functionaliteit: teksten, nieuwsberichten, video's, documenten publiceren
- Menustructuur aanpasbaar door functioneel beheerder
- Foutmeldingen en tooltips configureerbaar (zonder code-aanpassing)

### 10. Documenten delen (EIS)
- Upload van DPIA's, verwerkersovereenkomsten, pentesten per pakket
- Status: concept / gepubliceerd
- Zichtbaarheid: publiek / alleen gemeenten / privé

### 11. Management Informatie (EIS)
- Directe database-toegang voor rapportage-tool (bijv. Metabase, PowerBI)
- Matomo voor webstatistieken

### 12. API (EIS)
- **Publieke API** (GET): aanbodinformatie, pakketten, standaarden, organisaties
- **Beveiligde API** (CRUD met auth): gebruik-informatie, eigen registraties
- OpenAPI 3.x specificatie, API-first development
- Conform **NL API Strategie** (api-docs.nl)
- Versiebeheer: URI-versioning (/api/v1/)

### 13. Data-migratie (EIS)
- Migratie van bestaande Drupal-database (CSV + DB export) naar nieuw datamodel
- Binnen 2 dagen uitvoerbaar
- Validatie en rapportage van migratie
- Referentiële integriteit behouden (GUID-mapping)

---

## Niet-Functionele Eisen (verplicht)

### Beveiliging
- HTTPS/TLS voor alle communicatie
- 2FA verplicht voor alle beheeraccounts
- Data uitsluitend binnen EER (Europese Economische Ruimte)
- nl.internet.nl websitetest: **100% score** (HSTS, DNSSEC, TLS, IPv6, etc.)
- DKIM + DMARC voor e-mail
- Audit logging van alle activiteiten

### Toegankelijkheid
- **WCAG 2.1 AA** compliant (digitoegankelijk.nl)
- Responsive design (mobiel/tablet/desktop)
- Duidelijke foutmeldingen en gebruikersfeedback

### Performance
- Pagina laadtijd < 2 seconden voor standaard overzichtspagina's
- Zoekresultaten < 500ms

### Open Source
- Alle maatwerk: **EUPL-1.2 licentie**
- Broncode publiek beschikbaar (GitHub/GitLab)
- Goed gedocumenteerde code + README
- Geautomatiseerde tests (unit + integratie)

### Infrastructuur
- **OTAP** omgeving (Ontwikkel, Test, Acceptatie, Productie)
- Containerized (Docker/Kubernetes, Haven-compatibel)
- Geautomatiseerde deployments (CI/CD)
- Monitoring en alerting

### Informatiemodel
- Gebaseerd op **Informatiemodel Voorzieningencatalogus** (alliantie VNG)

---

## Functionele Wensen (nice-to-have, later te implementeren)

Implementeer alleen na voltooiing van alle eisen:

- **AI-advisering**: AI-gebaseerde aanbevelingen voor pakketkeuze (story 11, 43)
- **Dienstverleners**: Zoeken op aangeboden diensten (story 12)
- **Import vanuit spreadsheet**: Bewerkte export weer importeren (story 13)
- **Cloud-provider registratie** voor SaaS (story 14)
- **BIO beveiligingseisen**: Per pakket beveiligingsmaatregelen vastleggen (stories 49-52)
- **Vergelijken pakketten**: Side-by-side vergelijking (story 21)
- **Koppelingendiagram**: Visueel diagram informatiestromen (story 45)
- **Reviews/ratings**: Gemeenten kunnen pakketten beoordelen (story 46)
- **GT Inkoop**: Collectieve afspraken registreren (stories 47-48)
- **CMDB integratie**: Sync met externe bronnen (story 44)
- **Common Ground**: Aansluiting doelen/principes registreren (story 28)
- **Configureerbare filters** door functioneel beheerder (story 25)
- **Rol-specifieke startpagina's** (story 26)
- **Impersonatie** functioneel beheerder (story 85) — dit is wel relatief eenvoudig

---

## Projectstructuur

```
softwarecatalogus/
├── CLAUDE.md                    # Dit bestand
├── README.md
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
│
├── backend/                     # Django applicatie
│   ├── manage.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── Dockerfile
│   ├── config/                  # Django settings
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   ├── production.py
│   │   │   └── test.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── core/                # Gedeelde modellen, utils
│   │   ├── organisaties/        # Organisatie, contactpersonen
│   │   ├── pakketten/           # Pakket, PakketGebruik, Koppeling
│   │   ├── standaarden/         # Standaard, PakketStandaard
│   │   ├── architectuur/        # GemmaComponent, ArchiMate import/export
│   │   ├── documenten/          # Document uploads
│   │   ├── gebruikers/          # User, rollen, 2FA
│   │   ├── content/             # CMS: teksten, nieuws
│   │   ├── api/                 # API views, serializers, routers
│   │   └── migratie/            # Data-migratie tools
│   └── tests/
│
├── frontend/                    # Next.js applicatie
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   ├── Dockerfile
│   ├── src/
│   │   ├── app/                 # Next.js App Router
│   │   │   ├── (public)/        # Publieke pagina's
│   │   │   │   ├── page.tsx     # Homepage
│   │   │   │   ├── pakketten/   # Catalogus
│   │   │   │   └── organisaties/
│   │   │   ├── (auth)/          # Login, registratie, 2FA
│   │   │   └── (dashboard)/     # Ingelogde gebruikers
│   │   │       ├── mijn-landschap/    # Pakketoverzicht gemeente
│   │   │       ├── aanbod/            # Pakketbeheer leverancier
│   │   │       ├── beheer/            # Functioneel beheerder
│   │   │       └── profiel/
│   │   ├── components/
│   │   │   ├── ui/              # shadcn/ui componenten
│   │   │   ├── pakketten/
│   │   │   ├── architectuur/    # GEMMA kaart visualisatie
│   │   │   └── layout/
│   │   ├── lib/
│   │   │   ├── api.ts           # API client
│   │   │   └── utils.ts
│   │   ├── hooks/
│   │   └── types/               # TypeScript types (gegenereerd van OpenAPI)
│   └── public/
│
├── docs/                        # Technische documentatie
│   ├── api/                     # OpenAPI specs
│   ├── architectuur/
│   └── migratie/
│
└── infra/                       # Infrastructure as Code
    ├── k8s/                     # Kubernetes manifests
    └── scripts/                 # Deploy scripts
```

---

## Ontwikkelstrategie en Aanpak

### Fase 1: Fundament (begin hier)
1. **Docker setup**: docker-compose met Django, PostgreSQL, Redis, Meilisearch, Nginx
2. **Django project**: settings, auth (met 2FA), basis user model
3. **Datamodel**: Alle core modellen aanmaken met migraties
4. **API basis**: DRF + drf-spectacular, authenticatie endpoints
5. **Frontend basis**: Next.js setup, routing, auth flow, layout

### Fase 2: Kernfunctionaliteiten
6. **Pakketcatalogus**: Zoeken, filteren, detailpagina's (publiek)
7. **Organisatie-registratie**: Zelfregistratie leveranciers en gemeenten
8. **Pakketregistratie**: Aanbod-beheerder CRUD voor pakketten
9. **Gebruik registreren**: Gebruik-beheerder voegt pakketten toe aan landschap

### Fase 3: Geavanceerde features
10. **GEMMA integratie**: ArchiMate import/export, architectuurkaart visualisatie
11. **Standaarden**: Koppeling pakketten aan standaarden
12. **Documenten**: Upload en delen DPIA's etc.
13. **Export**: CSV, Excel, AMEFF exports

### Fase 4: Beheer en Admin
14. **Functioneel beheer**: Org-beheer, fiatteringen, CMS, configuratie
15. **2FA**: Volledig geïmplementeerd voor alle beheeraccounts
16. **Management info**: DB-toegang voor rapportage

### Fase 5: Kwaliteit en Productie
17. **Tests**: Unit + integratie tests
18. **Toegankelijkheid**: WCAG 2.1 AA audit en fixes
19. **Beveiliging**: nl.internet.nl 100% score
20. **Data-migratie**: Migratie van bestaande Drupal data
21. **OTAP**: Deployment naar test/acceptatie omgeving

---

## API Structuur (NL API Strategie)

Alle endpoints onder `/api/v1/`

### Publieke endpoints (geen auth vereist)
```
GET  /api/v1/pakketten/                 # Lijst pakketten (zoek/filter)
GET  /api/v1/pakketten/{id}/            # Pakket detail
GET  /api/v1/organisaties/              # Leveranciers lijst
GET  /api/v1/organisaties/{id}/         # Organisatie detail
GET  /api/v1/standaarden/              # Standaarden lijst
GET  /api/v1/gemma/componenten/        # GEMMA componenten
GET  /api/v1/gemma/componenten/{id}/   # GEMMA component detail
```

### Authenticatie
```
POST /api/v1/auth/login/               # Login (email + password)
POST /api/v1/auth/token/verify-totp/   # TOTP verificatie (2FA)
POST /api/v1/auth/logout/
POST /api/v1/auth/wachtwoord-reset/
POST /api/v1/auth/registreer/
```

### Beveiligde endpoints (auth vereist)
```
# Gebruik beheer
GET  /api/v1/mijn-organisatie/pakketoverzicht/
POST /api/v1/mijn-organisatie/pakketoverzicht/
DEL  /api/v1/mijn-organisatie/pakketoverzicht/{id}/
POST /api/v1/mijn-organisatie/koppelingen/
GET  /api/v1/gemeenten/{id}/pakketoverzicht/    # Gluren bij de buren

# Aanbod beheer (leverancier)
POST /api/v1/pakketten/                         # Nieuw pakket
PUT  /api/v1/pakketten/{id}/
POST /api/v1/pakketten/{id}/standaarden/
POST /api/v1/pakketten/{id}/documenten/

# Export
GET  /api/v1/export/pakketoverzicht.xlsx
GET  /api/v1/export/pakketoverzicht.csv
GET  /api/v1/export/pakketoverzicht.ameff

# Admin (functioneel beheerder)
GET  /api/v1/admin/organisaties/concept/
POST /api/v1/admin/organisaties/{id}/fiatteren/
POST /api/v1/admin/organisaties/samenvoegen/
GET  /api/v1/admin/gebruikers/
POST /api/v1/admin/gemma/importeer/              # AMEFF import

# Management info
GET  /api/v1/admin/statistieken/
```

---

## Authenticatie & Autorisatie Details

### Login Flow
1. POST email + wachtwoord → ontvang tijdelijk token
2. POST TOTP code → ontvang JWT access + refresh token
3. JWT meesturen in Authorization: Bearer header

### Registratie Flow (nieuwe gebruiker)
1. Gebruiker vult registratieformulier in (naam, email, organisatie-keuze)
2. Account aangemaakt met status 'wacht_op_fiattering'
3. Beheerder van organisatie ontvangt notificatie
4. Na fiattering: welkomstmail + TOTP setup

### Registratie Flow (nieuwe organisatie)
1. Aanbod/gebruik-beheerder registreert zichzelf + organisatie
2. Organisatie krijgt status 'concept'
3. Functioneel beheerder van VNG-R fiatteringen + activeert
4. Eerste beheerder van organisatie mag daarna zelf gebruikers toevoegen

---

## GEMMA ArchiMate Integratie

### Import
- Functioneel beheerder uploadt AMEFF-bestand (XML)
- Systeem parseert ArchiMate-model:
  - ApplicationComponent → GemmaComponent
  - ApplicationService → GemmaService
  - Relationships → hiërarchie en relaties
- Bestaande koppelingen pakket↔component blijven behouden
- Conflicten (hernoemde componenten) worden gerapporteerd

### Export (AMEFF)
- Gebruik-beheerder exporteert eigen pakketlandschap
- Bevat: pakketten → GEMMA-componenten → koppelingen
- Importeerbaar in Archi, Sparx EA, BiZZdesign

### Architectuurkaart Visualisatie
- Interactieve weergave van GEMMA-kaart (SVG/Canvas)
- Pakketten geplot op bijbehorende GEMMA-componenten
- Kleurcodering voor: in gebruik / gepland / verouderd
- Zoom en pan functionaliteit

---

## Zoekfunctionaliteit (Meilisearch)

### Geïndexeerde velden
- Pakketten: naam, beschrijving, leverancier.naam, gemma_componenten.naam, standaarden.naam
- Organisaties: naam, type

### Filters
- type_organisatie (gemeente / leverancier / samenwerkingsverband)
- standaard (ID of naam)
- gemma_component (ID)
- licentievorm
- in_gebruik_bij_gemeente (boolean)
- status

### Sortering
- Relevantie (default bij zoekopdracht)
- Naam (A-Z, Z-A)
- Populariteit (aantal gemeenten dat het gebruikt)
- Datum bijgewerkt

---

## Data-migratie

De bestaande Softwarecatalogus draait op Drupal. De data is beschikbaar als:
1. Database export (MySQL/PostgreSQL)
2. CSV exports met GUID-relaties

### Migratie-aanpak
- Schrijf een Django management command: `migrate_from_drupal`
- Map Drupal node-types naar nieuwe modellen:
  - `node:software` → `Pakket`
  - `node:organisation` → `Organisatie`
  - `node:relation` → `Koppeling` / `PakketGebruik`
- Bewaar originele GUID als `legacy_id` veld op alle modellen
- Valideer referentiële integriteit voor én na migratie
- Logging naar bestand: welke records geslaagd/mislukt
- Droog-run mode beschikbaar (`--dry-run`)

---

## Kwaliteitseisen

### Tests
- Minimaal 80% code coverage
- Unit tests voor alle business logic
- Integratie tests voor alle API endpoints
- Frontend: React Testing Library voor componenten

### Toegankelijkheid
- Gebruik aria-labels, role attributen, focus management
- Toetsenbordnavigatie volledig functioneel
- Voldoende kleurcontrast (WCAG AA)
- Screen reader compatibel

### Beveiliging
- Geen secrets in code (gebruik .env)
- SQL injection bescherming (ORM)
- XSS bescherming (React escaping + CSP headers)
- CSRF bescherming (Django standaard)
- Rate limiting op API endpoints
- Input validatie op frontend én backend

---

## Startinstructies voor Claude Code

### Stap 1: Start met het fundament
```bash
# Maak de volledige projectstructuur aan
# Stel docker-compose in met alle services
# Initialiseer Django project met correcte settings
# Maak User model met 2FA support
```

### Stap 2: Implementeer datamodellen
```bash
# Maak alle Django modellen aan (zie datamodel sectie)
# Schrijf database migraties
# Voeg fixtures toe voor testdata (GEMMA componenten, standaarden)
```

### Stap 3: Bouw de API
```bash
# DRF serializers en viewsets voor alle modellen
# Authenticatie endpoints (login, 2FA, registratie)
# OpenAPI spec via drf-spectacular
# Meilisearch indexering
```

### Stap 4: Frontend
```bash
# Next.js App Router setup
# Genereer TypeScript types van OpenAPI spec
# Publieke cataloguspagina's (zoeken, filteren, detail)
# Auth flow (login, 2FA, registratie)
# Dashboard voor gebruik-beheerder
# Dashboard voor aanbod-beheerder
```

### Stap 5: GEMMA & ArchiMate
```bash
# ArchiMate AMEFF XML parser
# GEMMA componenten database vullen
# Architectuurkaart visualisatie (SVG/Canvas)
# AMEFF export
```

---

## Omgevingsvariabelen (.env.example)

```env
# Database
DATABASE_URL=postgresql://swc:swc@db:5432/softwarecatalogus

# Redis
REDIS_URL=redis://redis:6379/0

# Meilisearch
MEILISEARCH_URL=http://meilisearch:7700
MEILISEARCH_API_KEY=your_master_key

# Django
SECRET_KEY=change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (DKIM/DMARC vereist in productie)
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=no-reply@softwarecatalogus.nl
EMAIL_HOST_PASSWORD=

# Storage (productie: S3-compatibel)
MEDIA_ROOT=/app/media
# AWS_STORAGE_BUCKET_NAME=
# AWS_S3_ENDPOINT_URL=

# Matomo
MATOMO_URL=https://matomo.softwarecatalogus.nl
MATOMO_SITE_ID=1

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MATOMO_URL=https://matomo.softwarecatalogus.nl
```

---

## Belangrijke Referenties

- **GEMMA Online**: https://www.gemmaonline.nl/
- **Informatiemodel Voorzieningencatalogus**: https://alliantie.informatiemodel.nl/ (of vergelijkbaar)
- **NL API Strategie**: https://docs.geostandaarden.nl/api/API-Strategie/
- **Forum Standaardisatie**: https://www.forumstandaardisatie.nl/
- **digitoegankelijk**: https://www.digitoegankelijk.nl/
- **nl.internet.nl**: https://nl.internet.nl/
- **Haven platform**: https://haven.commonground.nl/
- **EUPL licentie**: https://eupl.eu/

---

## Notities voor de Ontwikkelaar

1. **MVP eerste**: Implementeer alle *Eisen* (Eis) voor alle andere features
2. **API-first**: Schrijf eerst de OpenAPI spec, daarna de implementatie
3. **Open source**: Alle code moet EUPL-1.2 licensed zijn, geen proprietary dependencies
4. **Nederlands**: UI, foutmeldingen en documentatie in het Nederlands
5. **GEMMA is cruciaal**: De ArchiMate/GEMMA integratie is een kernfunctie, niet optioneel
6. **Concept-status patroon**: Consequent toepassen — alles aangemaakt door niet-eigenaar krijgt concept-status
7. **Datamodel is leidend**: Het Informatiemodel Voorzieningencatalogus is de bron van waarheid
8. **Security by design**: 2FA, audit logging, EER-datapositie van begin af aan

---

*Opgesteld op basis van VNG Realisatie aanbestedingsdocumentatie (oktober 2024)*
*Europese aanbesteding TN492936 — Vernieuwing Softwarecatalogus*
