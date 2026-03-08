# Architectuur — Softwarecatalogus

## Systeemoverzicht

```
┌─────────────────────────────────────────────────────────────────┐
│                    Internet / Gebruikers                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS
                    ┌──────▼──────┐
                    │    Nginx     │  (Reverse Proxy + SSL Termination)
                    └──────┬──────┘
              ┌────────────┴────────────┐
              │                         │
       ┌──────▼──────┐          ┌──────▼──────┐
       │  Next.js    │          │   Django    │
       │  Frontend   │◄────────►│   Backend   │
       │  (SSR/SSG)  │  API     │   (DRF)     │
       └─────────────┘          └──────┬──────┘
                                       │
              ┌────────────────────────┼──────────────────────┐
              │                        │                       │
       ┌──────▼──────┐        ┌────────▼────┐        ┌────────▼────┐
       │ PostgreSQL  │        │ Meilisearch │        │   Redis     │
       │  Database   │        │  (Zoeken)   │        │  (Cache +   │
       │             │        │             │        │   Celery)   │
       └─────────────┘        └─────────────┘        └─────────────┘
```

## Componenten

### Frontend (Next.js)
- **Server-Side Rendering** voor publieke pagina's (SEO)
- **Client-Side** voor dashboard/beheer functies
- Communiceert uitsluitend via REST API met backend
- Matomo tracking script

### Backend (Django)
- **REST API** via Django REST Framework
- **Authenticatie**: JWT tokens + 2FA (TOTP)
- **Business logic**: validatie, workflow, rechten
- **Celery workers**: async taken (import/export, email)
- **Meilisearch sync**: indexeert wijzigingen real-time

### Database (PostgreSQL)
- Primaire dataopslag
- Leestoegang voor externe rapportage-tools (read-only user)
- Dagelijkse backups

### Meilisearch
- Full-text zoeken over pakketten en organisaties
- Filters, facets, typo-tolerant zoeken
- Gesynchroniseerd via Django signals

### Redis
- Celery broker en result backend
- Session cache
- Rate limiting

## Deployment (OTAP)

```
Ontwikkel  → lokaal (docker-compose)
Test       → cloud (geautomatiseerd via CI/CD)
Acceptatie → cloud (review door VNG-R team)
Productie  → cloud (publiek toegankelijk)
```

### Haven-compatibiliteit
- Alle componenten als Docker containers
- Kubernetes manifests in /infra/k8s/
- Helm charts voor eenvoudige deployment

## Beveiliging in lagen

```
1. Netwerk:    HTTPS/TLS, HSTS, DNSSEC, IPv6
2. Applicatie: JWT auth, 2FA, RBAC, CSRF, XSS protection
3. Data:       Versleuteling at rest, EER-dataopslag
4. Monitoring: Audit logs, Sentry error tracking
5. Email:      DKIM + DMARC
```

## API Versioning

- URI-based: `/api/v1/`, `/api/v2/`
- OpenAPI 3.x spec beschikbaar op `/api/v1/schema/`
- Swagger UI op `/api/v1/docs/`
- ReDoc op `/api/v1/redoc/`

## Performance Strategie

- **Caching**: Django cache framework (Redis) voor zware queries
- **Database indexes**: op veelgebruikte filtervelden
- **Pagination**: cursor-based voor grote datasets
- **Lazy loading**: frontend laadt data on-demand
- **CDN**: statische assets via CDN in productie

## GEMMA ArchiMate Data Flow

```
AMEFF XML Upload
      │
      ▼
ArchiMate Parser (Python xml.etree)
      │
      ▼
GemmaComponent modellen (upsert op basis van archimate_id)
      │
      ├──► Bestaande PakketGemmaComponent relaties behouden
      │
      └──► Conflictenrapport → functioneel beheerder

Pakket koppelen aan GemmaComponent
      │
      ▼
AMEFF Export Generator
      │
      ▼
.ameff XML bestand (downloadbaar)
```
