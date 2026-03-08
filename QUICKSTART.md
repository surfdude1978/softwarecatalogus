# Quickstart — Softwarecatalogus

## Hoe te beginnen met Claude Code

Start Claude Code in de map `softwarecatalogus/` en geef het volgende commando:

```
Begin met het bouwen van de Softwarecatalogus volgens de instructies in CLAUDE.md.
Start met Fase 1: het opzetten van de volledige projectstructuur, Docker setup,
Django backend en Next.js frontend fundament.
```

## Volgorde van implementatie

### Fase 1 — Fundament
1. `docker-compose.yml` met PostgreSQL, Redis, Meilisearch, Nginx
2. Django project initialiseren (apps structuur uit CLAUDE.md)
3. Custom User model met 2FA support (django-otp)
4. Next.js 14 project met TypeScript en Tailwind CSS
5. `.env.example` met alle benodigde variabelen

### Fase 2 — Datamodel & API
1. Alle Django modellen aanmaken (zie CLAUDE.md §Datamodel)
2. Database migraties uitvoeren
3. DRF serializers en viewsets
4. OpenAPI spec genereren (drf-spectacular)
5. Authenticatie endpoints (login, 2FA, registratie, wachtwoord-reset)

### Fase 3 — Frontend basis
1. Layout componenten (header, navigatie, footer)
2. Publieke cataloguspagina's (zoeken/filteren/detail)
3. Auth flow (login pagina, 2FA setup)
4. Dashboard skelet voor de verschillende rollen

### Fase 4 — Kernfunctionaliteiten
1. Pakketregistratie (aanbod-beheerder)
2. Gebruik registreren (gebruik-beheerder)
3. Organisatiebeheer (functioneel beheerder)
4. GEMMA ArchiMate import/export
5. Export naar CSV/Excel/AMEFF

### Fase 5 — Polish & Productie
1. Toegankelijkheid (WCAG 2.1 AA)
2. Tests (>80% coverage)
3. Beveiliging (nl.internet.nl 100%)
4. Data-migratie script
5. Deployment configuratie (OTAP)

## Referentie documenten in deze map

- `CLAUDE.md` — Volledige specificatie en instructies (begin hier)
- `USER_STORIES.md` — Alle user stories uit de aanbesteding
- `ARCHITECTURE.md` — Technische architectuurdiagrammen
- `QUICKSTART.md` — Dit bestand

## Aanbestedingsstukken (origineel)

Beschikbaar in `../Aanbestedingsstukken t.b.v. Tenderned/`:
- Beschrijvend document.docx
- Bijlage 1.1 Programma van eisen softwarecatalogus.docx
- Bijlage 1.2 - Programma van eisen.xlsx (alle user stories)
- Bijlage 2 - Hosting eisen Softwarecatalogus.docx
- Bijlage 8 - Opdracht plan van aanpak versie 0.4.docx
