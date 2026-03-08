# Softwarecatalogus

[![Licentie: EUPL-1.2](https://img.shields.io/badge/Licentie-EUPL--1.2-blue.svg)](LICENSE)
[![CI](https://github.com/vng-realisatie/softwarecatalogus/actions/workflows/ci.yml/badge.svg)](https://github.com/vng-realisatie/softwarecatalogus/actions/workflows/ci.yml)

Centraal platform voor Nederlandse gemeenten, samenwerkingsverbanden en leveranciers om software-applicaties te registreren, vergelijken en raadplegen. Het platform maakt deel uit van de [VNG Realisatie](https://vng.nl/) dienstverlening en is geïntegreerd met de [GEMMA-referentiearchitectuur](https://www.gemmaonline.nl/).

> **Aanbesteding**: VNG Realisatie TN492936 — Vernieuwing Softwarecatalogus
> **Opvolger van**: softwarecatalogus.nl (Drupal)

---

## Inhoudsopgave

- [Functionaliteit](#functionaliteit)
- [Tech stack](#tech-stack)
- [Snel starten](#snel-starten)
- [Ontwikkeling](#ontwikkeling)
- [Testdata en accounts](#testdata-en-accounts)
- [API](#api)
- [Deployen](#deployen)
- [Bijdragen](#bijdragen)
- [Licentie](#licentie)

---

## Functionaliteit

| Module | Beschrijving |
|--------|-------------|
| **Pakketcatalogus** | Zoeken, filteren en raadplegen van softwarepakketten |
| **Gebruik-overzicht** | Gemeenten registreren welke pakketten zij gebruiken |
| **"Gluren bij de buren"** | Pakketlandschap van andere gemeenten inzien |
| **GEMMA-integratie** | Pakketten koppelen aan ArchiMate-referentiecomponenten |
| **Standaarden** | Koppelen van pakketten aan Forum Standaardisatie-standaarden |
| **Export** | CSV, Excel (.xlsx) en AMEFF (ArchiMate Exchange) export |
| **Documenten** | DPIA's, verwerkersovereenkomsten en pentesten per pakket |
| **Gebruikersbeheer** | Rollen, 2FA (TOTP), organisatiefiattering |
| **CMS** | Nieuws en informatieapgina's beheren |

---

## Tech stack

| Laag | Technologie |
|------|------------|
| Backend | Python 3.12 · Django 5 · Django REST Framework · drf-spectacular |
| Database | PostgreSQL 16 |
| Zoeken | Meilisearch |
| Async | Celery · Redis |
| Auth | JWT · TOTP (django-otp) · django-allauth |
| Frontend | Next.js 14 (App Router) · TypeScript · Tailwind CSS · shadcn/ui |
| State | TanStack Query · Zustand |
| Infra | Docker · Kubernetes (Helm) · Nginx |
| CI/CD | GitHub Actions → ghcr.io → Helm deploy |

---

## Snel starten

### Vereisten

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) ≥ 4.x
- [Git](https://git-scm.com/)

### 1. Repository klonen

```bash
git clone https://github.com/vng-realisatie/softwarecatalogus.git
cd softwarecatalogus
```

### 2. Omgevingsvariabelen instellen

```bash
cp .env.example .env
# Pas indien gewenst waarden aan in .env
```

### 3. Containers starten

```bash
docker-compose up -d
```

Dit start: PostgreSQL, Redis, Meilisearch, Django (backend), Next.js (frontend) en Nginx.

### 4. Database initialiseren met voorbeelddata

```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py seed_data
```

### 5. Applicatie openen

| URL | Omschrijving |
|-----|-------------|
| http://localhost | Softwarecatalogus (frontend) |
| http://localhost/api/v1/docs/ | Swagger UI (API documentatie) |
| http://localhost:8000/admin/ | Django Admin |

---

## Ontwikkeling

### Backend (Django)

```bash
# Shell in de backend-container
docker-compose exec backend bash

# Tests draaien
docker-compose exec backend pytest

# Tests met coverage
docker-compose exec backend pytest --cov=apps --cov-report=term-missing

# Nieuwe migraties genereren
docker-compose exec backend python manage.py makemigrations

# Meilisearch herindexeren
docker-compose exec backend python manage.py reindex_search
```

### Frontend (Next.js)

De frontend draait in dev-modus met hot reload. Bestanden in `frontend/src/` worden automatisch opgepikt.

```bash
# Logs bekijken
docker-compose logs -f frontend

# Frontend container herstarten (na nieuwe route-bestanden)
docker-compose up -d --force-recreate frontend
```

### Projectstructuur

```
softwarecatalogus/
├── backend/               # Django applicatie
│   ├── apps/
│   │   ├── api/           # DRF views, serializers, routers
│   │   ├── architectuur/  # GEMMA/ArchiMate import/export
│   │   ├── content/       # CMS (nieuws, pagina's)
│   │   ├── documenten/    # Document uploads
│   │   ├── gebruikers/    # User model, 2FA
│   │   ├── migratie/      # Drupal-migratie tools
│   │   ├── organisaties/  # Organisatie, contactpersonen
│   │   ├── pakketten/     # Pakket, PakketGebruik, Koppeling
│   │   └── standaarden/   # Standaard, PakketStandaard
│   └── config/            # Django settings (base/dev/prod/test)
├── frontend/              # Next.js applicatie
│   └── src/
│       ├── app/           # App Router pagina's
│       │   ├── (public)/  # Publieke cataloguspagina's
│       │   ├── (auth)/    # Login, registratie, 2FA
│       │   └── (dashboard)/ # Beheer-dashboards
│       ├── components/    # React-componenten
│       ├── hooks/         # Custom React hooks
│       └── types/         # TypeScript types
├── demo/                  # Playwright demo-opnames
├── infra/
│   ├── k8s/helm/          # Kubernetes Helm chart
│   └── nginx/             # Nginx configuratie
└── docs/                  # Technische documentatie
```

---

## Testdata en accounts

Na `python manage.py seed_data` zijn de volgende accounts beschikbaar (wachtwoord overal: **`Welkom01!`**):

| Rol | E-mailadres | Organisatie |
|-----|-------------|-------------|
| Functioneel beheerder | admin@vngrealisatie.nl | VNG Realisatie |
| Gebruik-beheerder (gemeente) | j.jansen@utrecht.nl | Gemeente Utrecht |
| Aanbod-beheerder (leverancier) | verkoop@centric.eu | Centric |

> **Let op:** 2FA (TOTP) is standaard uitgeschakeld voor demo-accounts. In productie is 2FA verplicht voor beheeraccounts.

---

## API

De API volgt de [NL API Strategie](https://docs.geostandaarden.nl/api/API-Strategie/).

- **Base URL**: `/api/v1/`
- **Authenticatie**: JWT Bearer token
- **Documentatie**: `/api/v1/docs/` (Swagger UI)
- **Schema**: `/api/v1/schema/` (OpenAPI 3.x YAML)

### Publieke endpoints (geen auth)

```
GET  /api/v1/pakketten/              # Lijst + zoeken/filteren
GET  /api/v1/pakketten/{id}/         # Pakketdetail
GET  /api/v1/organisaties/           # Organisaties
GET  /api/v1/standaarden/            # Standaarden
GET  /api/v1/gemma/componenten/      # GEMMA-componenten
```

### Authenticatie

```
POST /api/v1/auth/login/             # Email + wachtwoord → temp token
POST /api/v1/auth/token/verify-totp/ # TOTP verificatie → JWT
POST /api/v1/auth/logout/
POST /api/v1/auth/registreer/
```

---

## Deployen

Het project is Kubernetes-ready en Haven-compatibel.

### OTAP omgevingen

| Omgeving | Trigger |
|----------|---------|
| Test | Push naar `main` branch |
| Acceptatie | Handmatige trigger in GitHub Actions |
| Productie | Handmatige trigger in GitHub Actions |

### Helm deployment

```bash
helm upgrade --install softwarecatalogus infra/k8s/helm \
  --namespace softwarecatalogus \
  --values infra/k8s/helm/values.yaml \
  --set image.tag=<versie>
```

### GitHub Secrets (vereist voor CI/CD)

| Secret | Beschrijving |
|--------|-------------|
| `REGISTRY_TOKEN` | GitHub Container Registry token |
| `KUBE_CONFIG` | Kubernetes kubeconfig (base64) |
| `SECRET_KEY` | Django SECRET_KEY (productie) |
| `DATABASE_URL` | PostgreSQL connection string |
| `MEILISEARCH_API_KEY` | Meilisearch master key |

---

## Bijdragen

Issues en pull requests zijn welkom. Gebruik de GitHub Issues voor bugs en feature requests.

1. Fork de repository
2. Maak een feature branch: `git checkout -b feature/mijn-feature`
3. Commit met duidelijke berichten
4. Open een Pull Request naar `main`

Alle bijdragen vallen onder de EUPL-1.2 licentie.

---

## Licentie

Copyright © 2024 VNG Realisatie BV

Dit project is gelicenseerd onder de **European Union Public Licence (EUPL) versie 1.2**.
Zie het [LICENSE](LICENSE) bestand voor de volledige licentietekst.

De EUPL-1.2 is compatibel met GPL v2/v3, AGPL v3, MPL v2 en andere open source licenties.
Meer informatie: [eupl.eu](https://eupl.eu/)
