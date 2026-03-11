# Software Bill of Materials (SBOM)

**Project:** Softwarecatalogus — VNG Realisatie
**Licentie:** EUPL-1.2
**Datum:** 2026-03-11
**Git ref:** `main`

---

## Infrastructuur

| Component | Versie | Functie |
|-----------|--------|---------|
| PostgreSQL | 16.13 | Primaire database |
| Redis | 7.4.8 | Cache / message broker |
| Meilisearch | 1.6.2 | Full-text zoekmachine |
| Nginx | latest | Reverse proxy |
| Docker Compose | v2 | Container-orchestratie |

---

## Backend — Python / Django

**Runtime:** Python 3.12+

### Kern

| Package | Versie | Licentie | Functie |
|---------|--------|----------|---------|
| Django | 5.1.15 | BSD-3 | Web framework |
| djangorestframework | 3.16.1 | BSD-3 | REST API |
| gunicorn | 22.0.0 | MIT | WSGI server |
| psycopg | 3.3.3 | LGPL-3.0 | PostgreSQL driver |
| psycopg-binary | 3.3.3 | LGPL-3.0 | PostgreSQL driver (binary) |

### API & documentatie

| Package | Versie | Licentie | Functie |
|---------|--------|----------|---------|
| drf-spectacular | 0.29.0 | BSD-3 | OpenAPI 3.x spec-generatie |
| django-filter | 24.3 | BSD-3 | API filtering |
| django-cors-headers | 4.9.0 | MIT | CORS headers |
| uritemplate | 4.2.0 | Apache-2.0 | URI templates (OpenAPI) |
| inflection | 0.5.1 | MIT | String inflection |
| jsonschema | 4.26.0 | MIT | JSON Schema validatie |

### Authenticatie & beveiliging

| Package | Versie | Licentie | Functie |
|---------|--------|----------|---------|
| djangorestframework-simplejwt | 5.5.1 | MIT | JWT tokens |
| django-allauth | 65.15.0 | MIT | Authenticatie flows |
| django-otp | 1.7.0 | BSD-2 | 2FA / TOTP |
| django-guardian | 2.4.0 | BSD-3 | Object-level permissions |
| cryptography | 45.0.7 | Apache-2.0 / BSD-3 | Cryptografische primitieven |
| cffi | 1.17.1 | MIT | Foreign function interface |
| PyJWT | 2.11.0 | MIT | JSON Web Tokens |
| qrcode | 7.4.2 | BSD-3 | QR-code generatie (2FA setup) |

### Async taken & caching

| Package | Versie | Licentie | Functie |
|---------|--------|----------|---------|
| celery | 5.6.2 | BSD-3 | Asynchrone taakverwerking |
| django-celery-beat | 2.9.0 | BSD-3 | Periodieke taken |
| redis | 5.3.1 | MIT | Redis client |
| kombu | 5.6.2 | BSD-3 | Messaging library (Celery) |
| amqp | 5.3.1 | BSD-3 | AMQP protocol (Celery) |
| billiard | 4.2.4 | BSD-3 | Multiprocessing (Celery) |
| vine | 5.1.0 | BSD-3 | Promises (Celery) |

### Zoeken

| Package | Versie | Licentie | Functie |
|---------|--------|----------|---------|
| meilisearch | 0.40.0 | MIT | Meilisearch Python client |

### Data-export & bestandsverwerking

| Package | Versie | Licentie | Functie |
|---------|--------|----------|---------|
| openpyxl | 3.1.5 | MIT | Excel (.xlsx) export |
| lxml | 5.4.0 | BSD-3 | XML/AMEFF parsing |
| Pillow | 10.4.0 | HPND | Beeldverwerking |

### AI-assistent (optioneel)

| Package | Versie | Licentie | Functie |
|---------|--------|----------|---------|
| anthropic | 0.84.0 | MIT | Claude API client |
| httpx | 0.28.1 | BSD-3 | HTTP client (anthropic) |
| pydantic | 2.12.5 | MIT | Data validatie (anthropic) |

### Utilities

| Package | Versie | Licentie | Functie |
|---------|--------|----------|---------|
| python-decouple | 3.8 | MIT | Omgevingsvariabelen |
| django-extensions | 3.2.3 | MIT | Developer utilities |
| django-timezone-field | 7.2.1 | BSD-2 | Tijdzone velden |
| python-dateutil | 2.9.0 | Apache-2.0 / BSD-3 | Datumverwerking |
| requests | 2.32.5 | Apache-2.0 | HTTP client |
| PyYAML | 6.0.3 | MIT | YAML parsing |
| six | 1.17.0 | MIT | Python 2/3 compatibiliteit |

### Ontwikkeling & testen (niet in productie)

| Package | Versie | Licentie | Functie |
|---------|--------|----------|---------|
| pytest | 8.4.2 | MIT | Test runner |
| pytest-django | 4.12.0 | BSD-3 | Django test integratie |
| pytest-cov | 5.0.0 | MIT | Code coverage |
| coverage | 7.13.4 | Apache-2.0 | Coverage engine |
| factory-boy | 3.3.3 | MIT | Test fixtures |
| Faker | 40.8.0 | MIT | Testdata generatie |
| ruff | 0.15.5 | MIT | Linter / formatter |
| mypy | 1.19.1 | MIT | Static type checker |
| django-stubs | 5.2.9 | MIT | Django type stubs |
| django-debug-toolbar | 4.4.6 | BSD-3 | Debug toolbar |
| ipython | 8.38.0 | BSD-3 | Interactieve shell |

---

## Frontend — Next.js / TypeScript

**Runtime:** Node.js 18+

### Kern

| Package | Versie | Licentie | Functie |
|---------|--------|----------|---------|
| next | 14.2.21 | MIT | React framework (App Router) |
| react | ^18.3.1 | MIT | UI library |
| react-dom | ^18.3.1 | MIT | DOM rendering |

### State & data

| Package | Versie | Licentie | Functie |
|---------|--------|----------|---------|
| @tanstack/react-query | ^5.59.0 | MIT | Server state / data fetching |
| zustand | ^5.0.0 | MIT | Client state management |

### Styling & UI

| Package | Versie | Licentie | Functie |
|---------|--------|----------|---------|
| tailwindcss | ^3.4.0 | MIT | Utility-first CSS |
| autoprefixer | ^10.4.0 | MIT | CSS vendor prefixes |
| postcss | ^8.4.0 | MIT | CSS transformaties |
| lucide-react | ^0.447.0 | ISC | Iconen |
| class-variance-authority | ^0.7.0 | Apache-2.0 | Component variants (shadcn/ui) |
| clsx | ^2.1.1 | MIT | Class name merging |
| tailwind-merge | ^2.5.0 | MIT | Tailwind class deduplicatie |

### Export

| Package | Versie | Licentie | Functie |
|---------|--------|----------|---------|
| docx | ^9.6.0 | MIT | DOCX generatie |

### Ontwikkeling & testen (niet in productie)

| Package | Versie | Licentie | Functie |
|---------|--------|----------|---------|
| typescript | ^5.6.0 | Apache-2.0 | Type checking |
| eslint | ^8.57.0 | MIT | Linting |
| eslint-config-next | 14.2.21 | MIT | Next.js ESLint regels |
| jest | ^29.7.0 | MIT | Test runner |
| jest-environment-jsdom | ^29.7.0 | MIT | Browser-like test env |
| ts-jest | ^29.2.0 | MIT | TypeScript voor Jest |
| @testing-library/react | ^16.0.0 | MIT | Component tests |
| @testing-library/jest-dom | ^6.5.0 | MIT | DOM matchers |
| @testing-library/user-event | ^14.5.0 | MIT | User event simulatie |
| jest-axe | ^10.0.0 | MIT | Accessibility tests |
| @types/node | ^22.0.0 | MIT | Node.js type defs |
| @types/react | ^18.3.0 | MIT | React type defs |
| @types/react-dom | ^18.3.0 | MIT | ReactDOM type defs |
| @types/jest-axe | ^3.5.9 | MIT | jest-axe type defs |
| @jest/types | ^29.6.0 | MIT | Jest type defs |

---

## Licentie-samenvatting

| Licentie | Aantal packages | Compatibel met EUPL-1.2 |
|----------|----------------|--------------------------|
| MIT | ~75 | Ja |
| BSD-2 / BSD-3 | ~20 | Ja |
| Apache-2.0 | ~6 | Ja |
| LGPL-3.0 | 2 (psycopg) | Ja |
| ISC | 1 (lucide-react) | Ja |
| HPND | 1 (Pillow) | Ja |

Alle gebruikte licenties zijn compatibel met de EUPL-1.2 projectlicentie.

---

## Bijwerken van deze SBOM

Regenereer met:

```bash
# Backend
docker compose exec backend pip freeze | sort

# Frontend
cat frontend/package.json | jq '.dependencies, .devDependencies'

# Infrastructuur
docker compose exec db psql -U swc -c "SELECT version();" -t
docker compose exec redis redis-server --version
docker compose exec meilisearch meilisearch --version
```
