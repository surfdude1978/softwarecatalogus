# Softwarecatalogus — Productvisie, Roadmap & Kwaliteitsbaseline

> **Document type:** Product Management Reference
> **Eigenaar:** Product Manager / VNG Realisatie
> **Versie:** 1.0 — maart 2026
> **Status:** Levend document — wordt bijgehouden parallel aan de roadmap
> **Aanbesteding:** TN492936 — Vernieuwing Softwarecatalogus

---

## Inhoudsopgave

1. [Productvisie](#1-productvisie)
2. [Doelbeeld en scope](#2-doelbeeld-en-scope)
3. [Roadmap](#3-roadmap)
4. [Baseline productkwaliteit](#4-baseline-productkwaliteit)
5. [Meetbare kwaliteitscriteria en KPIs](#5-meetbare-kwaliteitscriteria-en-kpis)
6. [Huidige situatie en gap-analyse](#6-huidige-situatie-en-gap-analyse)
7. [Productvolwassenheid](#7-productvolwassenheid)
8. [Governance en eigenaarschap](#8-governance-en-eigenaarschap)
9. [Randvoorwaarden en afhankelijkheden](#9-randvoorwaarden-en-afhankelijkheden)
10. [Risicos en mitigaties](#10-risicos-en-mitigaties)
11. [Advies en besluitpunten](#11-advies-en-besluitpunten)

---

## 1. Productvisie

### 1.1 Het probleem

Nederlandse gemeenten en samenwerkingsverbanden beschikken niet over een betrouwbare, actuele en gedeelde registratie van de software die zij gebruiken. Gevolgen:

- **Fragmentatie**: elke gemeente beheert eigen lijstjes, niet vergelijkbaar, niet deelbaar.
- **Inefficiëntie bij inkoop**: gemeenten herontdekken het wiel bij aanbestedingen; kennis over bestaand gebruik blijft onbenut.
- **Architectuurblindheid**: de koppeling tussen software en de GEMMA-referentiearchitectuur bestaat nergens gestructureerd — waardoor architectuurbesluiten onvoldoende gefundeerd zijn.
- **Ongelijke informatiepositie**: leveranciers weten niet wie hun product gebruikt; gemeenten weten niet wat er in de markt beschikbaar is.
- **Verouderde infrastructuur**: de huidige Drupal-gebaseerde softwarecatalogus.nl is technisch verouderd, moeilijk onderhoudbaar en niet geïntegreerd met GEMMA Online.

### 1.2 De visie

> **De Softwarecatalogus is het centrale, gezaghebbende en openbare kennisplatform voor software bij Nederlandse gemeenten — waar aanbod, gebruik en architectuur samenkomen.**

Het platform maakt het voor gemeenten mogelijk om:
- snel te zien welke software beschikbaar is en welke gemeenten het gebruiken;
- hun eigen softwarelandschap te registreren en te vergelijken met vergelijkbare gemeenten;
- softwarekeuzes te verankeren in de GEMMA-referentiearchitectuur;
- documenten zoals DPIA's en pentesten te delen met de gemeentelijke gemeenschap.

Voor leveranciers biedt het een zichtbaar en gestructureerd kanaal om hun aanbod te presenteren aan de volledige doelgroep.

Voor VNG Realisatie verschaft het actueel inzicht in het applicatielandschap van alle gemeenten — onmisbaar voor beleid, inkoopondersteuning en standaardisatietrajecten.

### 1.3 Primaire en secundaire gebruikersgroepen

| Groep | Rol | Primair gebruik |
|---|---|---|
| **Gebruik-beheerder** (gemeente/SWV) | Primair | Eigen pakketlandschap registreren en beheren |
| **Aanbod-beheerder** (leverancier) | Primair | Pakketten registreren en actueel houden |
| **Functioneel beheerder** (VNG-R) | Primair | Platform beheren, fiatteren, rapporteren |
| **Aanbod-raadpleger** | Secundair | Catalogus doorzoeken, marktverkenning |
| **Gebruik-raadpleger** | Secundair | "Gluren bij de buren" — referentielandschappen bekijken |
| **IBD-beheerder** | Secundair | Beveiligingsstatus en BIO-eisen monitoren |
| **GT Inkoop-beheerder** | Secundair | Collectieve afspraken vastleggen |
| **Anonieme bezoeker** | Secundair | Publieke catalogus raadplegen |

### 1.4 Waardepropositie

| Dimensie | Waarde |
|---|---|
| **Gebruikers** | Tijdwinst bij oriëntatie, inkoop en aanbesteding; inzicht in wat anderen doen |
| **Governance** | Actueel en betrouwbaar beeld van het gemeentelijke applicatielandschap |
| **Architectuur** | Koppeling software ↔ GEMMA maakt architectuuranalyse mogelijk |
| **VNG Realisatie** | Stuurinformatie voor beleid, standaardisatie en collectieve inkoop |
| **Leveranciers** | Transparante marktzichtbaarheid; gestructureerde klantrelatie |

### 1.5 Positie in het informatielandschap

De Softwarecatalogus is een **registratieplatform**, geen procestool. Het complementeert:

- **GEMMA Online** (referentiearchitectuur) — de catalogus koppelt software aan GEMMA-componenten
- **Forum Standaardisatie** — standaarden worden gerefereerd, niet beheerd
- **Gemeentelijke CMDB's** — de catalogus ontvangt data, is geen vervanging
- **TenderNed** — aanbestedingsinformatie kan gekoppeld worden voor context
- **Common Ground** — principes en doelen zijn verbonden, niet gedupliceerd

> **Aanname:** De catalogus positioneert zich als *bron* voor gemeentelijk applicatiegebruik, niet als gezaghebbende bron voor softwareeigenschappen (die blijft bij leveranciers zelf).

### 1.6 Leidende productprincipes

1. **Actualiteit boven volledigheid** — een actuele subset is waardevoller dan een verouderd compleet overzicht.
2. **Open tenzij bewust gesloten** — alle basisinformatie is publiek toegankelijk; enkel gevoelige data is afgeschermd.
3. **GEMMA-verankering is geen optie** — architectuurkoppeling is kernfunctie, niet nice-to-have.
4. **Eenvoud voor de beheerder** — een gebruik-beheerder moet zonder opleiding zijn landschap kunnen bijhouden.
5. **API-first** — alle functionaliteit is via de API beschikbaar; de UI is een implementatie daarvan.
6. **Nederlandse standaarden** — NL API Strategie, WCAG 2.1 AA, EUPL-1.2, nl.internet.nl 100%.
7. **Open source by default** — broncode onder EUPL-1.2, publiek op GitHub.

---

## 2. Doelbeeld en scope

### 2.1 Kernfunctionaliteiten (binnen scope, verplicht)

| # | Functionaliteit | Status |
|---|---|---|
| K1 | Pakketcatalogus: zoeken, filteren, detailpagina's | ✅ Geïmplementeerd |
| K2 | Pakketregistratie door aanbod-beheerder (leverancier) | ✅ Geïmplementeerd |
| K3 | Gebruik registreren door gebruik-beheerder (gemeente) | ✅ Geïmplementeerd |
| K4 | GEMMA ArchiMate import/export (AMEFF) | ✅ Geïmplementeerd |
| K5 | Architectuurkaart — pakketten op GEMMA-kaart | ✅ Geïmplementeerd |
| K6 | Export CSV, Excel, AMEFF | ✅ Geïmplementeerd |
| K7 | Organisatiebeheer met fiatteerstroom | ✅ Geïmplementeerd |
| K8 | Gebruikers & toegang met 2FA (TOTP) | ✅ Geïmplementeerd |
| K9 | Documenten delen (DPIA's, pentesten) | ✅ Geïmplementeerd |
| K10 | Audit logging | ✅ Geïmplementeerd |
| K11 | Standaardenkoppeling (Forum Standaardisatie) | ✅ Geïmplementeerd |
| K12 | Publieke REST API (OpenAPI 3.x / NL API Strategie) | ✅ Geïmplementeerd |
| K13 | Zelfregistratie leveranciers + fiattering | ✅ Geïmplementeerd |
| K14 | Data-migratie vanuit Drupal | 🔲 Nog te implementeren |
| K15 | CMS voor nieuws, teksten, menu's | 🔲 Nog te implementeren |

### 2.2 Wenselijke functionaliteiten (binnen scope, lager prioriteit)

| # | Functionaliteit | Motivatie |
|---|---|---|
| W1 | Pakket vergelijken (side-by-side) | Vergroot beslisondersteuning |
| W2 | Reviews en ratings per pakket | Kennisdeling gemeenschap |
| W3 | Koppelingendiagram (informatiestromen visueel) | Architectuurinzicht |
| W4 | BIO beveiligingseisen per pakket | IBD-samenwerking |
| W5 | TenderNed koppeling (aanbestedingen) | Context bij pakketten |
| W6 | Import vanuit spreadsheet | Migratieverlichting |
| W7 | AI-gestuurde pakketaanbevelingen | Gebruiksgemak |
| W8 | GT Inkoop collectieve afspraken | VNG-samenwerking |
| W9 | nl.internet.nl 100% score (productie) | Security compliance |
| W10 | Matomo analytics (productie) | Gebruiksdata |

### 2.3 Expliciet buiten scope

- **Contractbeheer** — de catalogus registreert gebruik, niet contracten of SLA's.
- **Financieel beheer** — licentiekosten of budgetten worden niet bijgehouden.
- **Projectportfolio** — geen koppeling met projectmanagementtools.
- **CMDB-vervanger** — de catalogus synchroniseert optioneel, vervangt geen CMDB.
- **Certificering of goedkeuring van software** — de catalogus is neutraal; geen keurmerk.
- **Beheer van GEMMA Online** — de catalogus leest GEMMA, beheert het niet.

### 2.4 Minimale levensvatbare invulling (MVP)

Het MVP is bereikt wanneer:
1. Een gebruik-beheerder zijn pakketlandschap kan registreren en exporteren.
2. Een aanbod-beheerder pakketten kan registreren en koppelen aan GEMMA.
3. Een anonieme bezoeker de catalogus kan doorzoeken.
4. Alle data is gekoppeld aan GEMMA-componenten.
5. 2FA is verplicht voor alle beheeraccounts.
6. De API voldoet aan NL API Strategie.

> **Conclusie:** Het MVP is voor de kernfunctionaliteiten (K1–K13) nagenoeg bereikt. K14 (Drupal-migratie) en K15 (CMS) zijn de resterende MVP-items.

### 2.5 Middellange termijn ambitie (12–18 maanden)

- Alle W-items geïmplementeerd of bewust gedefer'd.
- Volledige Drupal-migratie uitgevoerd, oud systeem afgeschakeld.
- nl.internet.nl 100% score behaald.
- Adoptie: >80% van gemeenten heeft minimaal één pakket geregistreerd.
- Matomo-data beschikbaar voor stuurinformatie.

---

## 3. Roadmap

### Fasering

```
2026 Q1  │ Fase A: Stabilisatie & Productionisering
2026 Q2  │ Fase B: Adoptie & Datakwaliteit
2026 Q3  │ Fase C: Doorontwikkeling & Integratie
2026 Q4+ │ Fase D: Volwassenheid & Strategie
```

---

### Fase A — Stabilisatie & Productionisering (Q1 2026, lopend)

**Beoogd resultaat:** Het platform is productie-klaar, stabiel en veilig. Bestaande data is gemigreerd.

**Epics / thema's:**

| Epic | Issues | Prioriteit | Reden |
|---|---|---|---|
| A1 — Security hardening | #5 (2FA bypass), #6 (JWT/httpOnly), #39 (rate limiting) | 🔴 Kritiek | Open kwetsbaarheden in productie |
| A2 — OpenAPI schema publicatie | #38 | 🟠 Hoog | API-first principe; externe integraties blokkeren |
| A3 — Frontend toegankelijkheid tests | #37 | 🟠 Hoog | WCAG 2.1 AA is wettelijke verplichting |
| A4 — Matomo activeren | #35 | 🟡 Gemiddeld | Geen gebruiksinzicht zonder analytics |
| A5 — CMS / configureerbaar menu | #34 | 🟡 Gemiddeld | Functioneel beheerder heeft handmatige workaround nodig |
| A6 — Drupal data-migratie | Nieuw issue | 🔴 Kritiek | Bestaande catalogus moet afgeschakeld worden |

**Afhankelijkheden:**
- A1 vereist productieomgeving draaiend (✅ Hetzner server beschikbaar)
- A6 vereist toegang tot Drupal database export (⚠️ aanname: VNG levert dit aan)

**Risico's:**
- Drupal-migratie kan complexer zijn dan verwacht door datakwaliteitsproblemen in brondata.
- 2FA-hardening (A1) kan bestaande gebruikers blokkeren als rollout niet zorgvuldig gepland.

**Aannames:**
- ⚠️ *Aanname:* De Hetzner server is de productieomgeving voor de komende 6+ maanden (geen Kubernetes-migratie op korte termijn).
- ⚠️ *Aanname:* VNG Realisatie levert binnen Q1 2026 een Drupal database dump aan voor migratie.

---

### Fase B — Adoptie & Datakwaliteit (Q2 2026)

**Beoogd resultaat:** Gemeenten en leveranciers zijn actief. Datakwaliteit is meetbaar en geborgd.

**Epics / thema's:**

| Epic | Issues / Thema's | Prioriteit | Reden |
|---|---|---|---|
| B1 — Onboarding leveranciers | Nieuw | 🔴 Kritiek | Catalogus heeft geen waarde zonder aanboddata |
| B2 — Onboarding gemeenten (top 25) | Nieuw | 🔴 Kritiek | Gebruik-data is de unieke waarde van de catalogus |
| B3 — nl.internet.nl 100% | #15, #23 | 🟠 Hoog | Wettelijke/governance eis |
| B4 — TenderNed koppeling | #4, #14, #22 | 🟡 Gemiddeld | Context verrijking; afhankelijk van TenderNed API |
| B5 — GEMMA-component filter verbetering | #50 | 🟡 Gemiddeld | Kernzoekopdracht voor architecten |
| B6 — Datakwaliteitsmonitoring | Nieuw | 🟡 Gemiddeld | Zonder monitoring degradeert data snel |

**Afhankelijkheden:**
- B1/B2 vereisen communicatiecampagne vanuit VNG Realisatie.
- B3 vereist DNS-configuratie met DNSSEC en IPv6 op domeinnaam (buiten code-scope).
- B4 is afhankelijk van TenderNed API-beschikbaarheid.

**Risico's:**
- Lage adoptie als beheerders het systeem als last ervaren (zie governance sectie).
- Datakwaliteit degradeert als er geen validatie- en attenderings-processen zijn.

---

### Fase C — Doorontwikkeling & Integratie (Q3 2026)

**Beoogd resultaat:** Het platform biedt rijkere beslisondersteuning en diepere GEMMA-integratie.

**Epics / thema's:**

| Epic | Issues | Prioriteit | Reden |
|---|---|---|---|
| C1 — Pakket vergelijken | #30 | 🟡 Gemiddeld | Hogere waarde bij aanbestedingsondersteuning |
| C2 — Koppelingendiagram visueel | #31 | 🟡 Gemiddeld | Architectuurinzicht; vraag vanuit gemeenten |
| C3 — BIO beveiligingseisen per pakket | #33 | 🟠 Hoog | IBD-samenwerking; securitybaseline |
| C4 — Reviews en ratings | #32 | 🟡 Gemiddeld | Kennisdeling; waarde stijgt met adoptie |
| C5 — Import vanuit spreadsheet | Nieuw | 🟡 Gemiddeld | Drempelverlaagend voor onboarding |
| C6 — CMDB-sync prototype | Nieuw | 🔵 Laag | Strategisch; begin met één gemeente als pilot |

**Aannames:**
- ⚠️ *Aanname:* Reviews/ratings vereisen moderatieproces en governance-besluit over anonimiteit.
- ⚠️ *Aanname:* C6 vereist medewerking van minimaal één gemeente die een CMDB-koppeling wil piloten.

---

### Fase D — Volwassenheid & Strategie (Q4 2026+)

**Beoogd resultaat:** Softwarecatalogus is de erkende standaard voor gemeentelijk applicatiebeheer.

**Strategische thema's:**

| Thema | Beschrijving |
|---|---|
| D1 — AI-advisering | Pakketaanbevelingen op basis van profiel gemeente + GEMMA |
| D2 — GT Inkoop integratie | Collectieve afspraken zichtbaar in catalogus |
| D3 — Kubernetes / Haven | Schaling en compliantie met Common Ground platformvereisten |
| D4 — Common Ground aansluiting | Principes en doelen verankerd in pakketten |
| D5 — Informatiemodel update | Doorontwikkeling datamodel bij wijziging VNG-standaard |

**Bewuste latere keuze:** D1 (AI) pas na voldoende datakwaliteit — AI op slechte data is contraproductief.

---

## 4. Baseline productkwaliteit

### 4.1 Functionele juistheid

| Niveau | Definitie |
|---|---|
| **Voldoende** | Alle EIS-items werken zoals gespecificeerd; geen blokkerende bugs in productie |
| **Goed** | <1% foutpercentage op alle API-aanroepen; 0 open kritieke bugs |
| **Norm** | Geautomatiseerde regressietests op alle EIS-scenario's |
| **Meetbaar** | Foutpercentage via monitoring; bugtracker met severity-classificatie |
| **Baseline-check** | Release-acceptatietest op alle EIS-items voor elke productiedeploy |

### 4.2 Gebruiksvriendelijkheid

| Niveau | Definitie |
|---|---|
| **Voldoende** | Primaire taken (registreer pakket, zoek pakket) uitvoerbaar zonder handleiding |
| **Goed** | Taakvoltooidheidsscore >85% in gebruikerstest; gebruikerstevredenheid ≥3.5/5 |
| **Norm** | WCAG 2.1 AA; responsive design (320px–1920px) |
| **Meetbaar** | Periodieke gebruikerstest (halfjaarlijks); Matomo task completion tracking |
| **Baseline-check** | WCAG-audit bij elke major release (geautomatiseerd + handmatig) |

### 4.3 Performance

| Niveau | Definitie |
|---|---|
| **Voldoende** | Overzichtspagina's laden <2s (P95, desktop, 4G); zoekresultaten <500ms |
| **Goed** | Core Web Vitals "Good" (LCP <2.5s, FID <100ms, CLS <0.1) |
| **Norm** | NL Webrichtlijnen performance; Lighthouse score ≥80 |
| **Meetbaar** | Lighthouse CI in GitHub Actions; APM monitoring op productie |
| **Baseline-check** | Lighthouse score check bij elke PR naar main |

### 4.4 Beschikbaarheid

| Niveau | Definitie |
|---|---|
| **Voldoende** | 99% uptime gemeten over kalendermaand (≤7.3u downtime/maand) |
| **Goed** | 99.5% uptime; geplande maintenance buiten kantooruren |
| **Norm** | SLA te bepalen met VNG Realisatie; initieel geen formele SLA |
| **Meetbaar** | Uptime monitoring (bijv. UptimeRobot of gelijkwaardig) |
| **Baseline-check** | Maandelijks uptime-rapport; incident-review bij >30min downtime |

> **Aanname:** ⚠️ Een formele SLA is er (nog) niet. Voldoende = 99% is een product management-aanname.

### 4.5 Betrouwbaarheid

| Niveau | Definitie |
|---|---|
| **Voldoende** | 0 dataverlies-incidenten; dagelijkse databasebackup met verificatie |
| **Goed** | Point-in-time recovery mogelijk; backup-restore getest per kwartaal |
| **Norm** | RPO ≤24u, RTO ≤4u (aanname, te valideren met VNG) |
| **Meetbaar** | Backup-logs; jaarlijkse DR-test |
| **Baseline-check** | Backup-verificatie automatisch na elke nachtelijke backup |

### 4.6 Beveiliging en privacy

| Niveau | Definitie |
|---|---|
| **Voldoende** | Geen open kritieke kwetsbaarheden (CVSS ≥9); 2FA verplicht voor beheer; HTTPS overal |
| **Goed** | nl.internet.nl 100%; dependency scanning actief; jaarlijkse pentest |
| **Norm** | BIO (Baseline Informatiebeveiliging Overheid); AVG-compliant; data in EER |
| **Meetbaar** | Snyk/Dependabot alerts; nl.internet.nl score; pentest-rapport |
| **Baseline-check** | Dependency scan bij elke PR; nl.internet.nl score maandelijks |

### 4.7 Actualiteit en volledigheid van gegevens

| Niveau | Definitie |
|---|---|
| **Voldoende** | >50% van actieve gemeenten heeft minimaal één pakket geregistreerd |
| **Goed** | >80% adoptie; pakketgegevens gemiddeld <12 maanden oud |
| **Norm** | Verloopdatum-herinnering na 12 maanden inactiviteit per pakket |
| **Meetbaar** | Adoptie-dashboard (Matomo + DB-query); ouderdomsrapportage |
| **Baseline-check** | Kwartaalrapportage adoptie aan product owner |

### 4.8 Beheerbaarheid

| Niveau | Definitie |
|---|---|
| **Voldoende** | Deploy in <15 minuten; rollback mogelijk binnen 5 minuten |
| **Goed** | Zero-downtime deploys; geautomatiseerde CI/CD; gestructureerde logging |
| **Norm** | Docker Compose productie; Kubernetes-gereed architectuur |
| **Meetbaar** | Deploy-tijden in CI/CD logs; rollback-tijd bij incident |
| **Baseline-check** | CI/CD pipeline groen vereist voor deploy naar productie |

### 4.9 Auditability / herleidbaarheid

| Niveau | Definitie |
|---|---|
| **Voldoende** | Alle schrijfacties (CREATE/UPDATE/DELETE) gelogd met user + timestamp |
| **Goed** | Audit log doorzoekbaar; retentie ≥2 jaar; export mogelijk |
| **Norm** | Conform BIO audit logging vereisten |
| **Meetbaar** | Audit log coverage in tests; steekproef bij kwartaalreview |
| **Baseline-check** | Geautomatiseerde test: elke API-mutatie produceert audit log entry |

### 4.10 Toegankelijkheid

| Niveau | Definitie |
|---|---|
| **Voldoende** | WCAG 2.1 AA voor alle publieke pagina's |
| **Goed** | Digitoegankelijk.nl verklaring gepubliceerd; periodieke audit |
| **Norm** | Wet digitale overheid; WCAG 2.1 AA (niveau A + AA) |
| **Meetbaar** | axe-core geautomatiseerde tests; handmatige audit halfjaarlijks |
| **Baseline-check** | jest-axe / axe-playwright in CI; blokkeerbaar bij kritieke WCAG-fouten |

### 4.11 Interoperabiliteit

| Niveau | Definitie |
|---|---|
| **Voldoende** | OpenAPI 3.x spec beschikbaar en accuraat; NL API Strategie gevolgd |
| **Goed** | AMEFF import/export gevalideerd met Archi en BiZZdesign; API versionering actief |
| **Norm** | NL API Strategie; ArchiMate 3.x AMEFF formaat; JSON/CSV/XLSX export |
| **Meetbaar** | API spec validatie in CI; AMEFF round-trip test (import→export→import) |
| **Baseline-check** | OpenAPI spec drift-detectie bij elke API-wijziging |

---

## 5. Meetbare kwaliteitscriteria en KPI's

### 5.1 Primaire KPI's (stuurinformatie)

| KPI | Doel | Drempelwaarde | Meting | Frequentie |
|---|---|---|---|---|
| **Adoptie gemeenten** | >80% heeft ≥1 pakket | <50% = actie | DB-query | Maandelijks |
| **API foutpercentage (5xx)** | <0.1% | >1% = incident | APM / logs | Continu |
| **Kritieke open bugs** | 0 | >0 = blokkeer release | GitHub Issues | Bij elke release |
| **Uptime** | ≥99.5% | <99% = SLA-breach | Uptime monitor | Maandelijks |
| **WCAG-fouten kritiek** | 0 | >0 = blokkeer release | axe-core CI | Per PR |
| **Dependency CVE critical** | 0 open | >0 = actie binnen 24u | Dependabot | Dagelijks |
| **Backup succes** | 100% | Mislukking = incident | Backup logs | Dagelijks |

### 5.2 Secundaire KPI's (ondersteunend)

| KPI | Doel | Meting | Frequentie |
|---|---|---|---|
| **Paginalaadtijd P95** | <2s | Lighthouse CI | Per PR |
| **Zoektijd P95** | <500ms | APM | Continu |
| **Test coverage backend** | ≥80% | pytest-cov in CI | Per PR |
| **TypeScript strict errors** | 0 | tsc --noEmit in CI | Per PR |
| **Gemiddelde leeftijd pakketdata** | <12 maanden | DB-query | Kwartaal |
| **Actieve beheerders per gemeente** | ≥1 | DB-query | Kwartaal |
| **Gebruikerstevredenheid** | ≥3.5/5 | Periodieke enquête | Halfjaarlijks |
| **nl.internet.nl score** | 100% | Handmatig / API | Maandelijks |

### 5.3 Acceptatiecriteria voor releases

Een release naar productie is toegestaan wanneer:
- [ ] Alle CI/CD checks groen (tests, lint, TypeScript, axe)
- [ ] 0 kritieke bugs open
- [ ] 0 kritieke WCAG-fouten
- [ ] 0 kritieke CVE's in dependencies
- [ ] Smoke test op staging geslaagd
- [ ] Rollback-procedure gedocumenteerd en getest

### 5.4 Incidentclassificatie en responstijden

| Klasse | Definitie | Responstijd | Oplostijd (doel) |
|---|---|---|---|
| **P1 — Kritiek** | Productie down of dataverlies | 30 min | 4 uur |
| **P2 — Hoog** | Kernfunctie onbruikbaar | 2 uur | 24 uur |
| **P3 — Gemiddeld** | Functie degraded, workaround beschikbaar | 1 werkdag | 5 werkdagen |
| **P4 — Laag** | Cosmetisch of minor | 1 week | Volgende sprint |

---

## 6. Huidige situatie en gap-analyse

### 6.1 Huidige productstatus (maart 2026)

| Onderdeel | Status | Toelichting |
|---|---|---|
| Backend Django | ✅ Operationeel | API draait, modellen stabiel |
| Frontend Next.js | ✅ Operationeel | Publieke pages + dashboard live |
| PostgreSQL | ✅ Operationeel | Productie op Hetzner |
| Meilisearch | ✅ Operationeel | Zoekindex actief |
| Redis + Celery | ✅ Operationeel | Async taken werken |
| GEMMA import/export | ✅ Geïmplementeerd | AMEFF parser aanwezig |
| Architectuurkaart | ✅ Geïmplementeerd | Visuele kaart live |
| Export CSV/XLSX/AMEFF | ✅ Geïmplementeerd | |
| 2FA (TOTP) | ✅ Geïmplementeerd | Verplicht voor beheer |
| Audit logging | ✅ Geïmplementeerd | Alle schrijfacties |
| CI/CD (GitHub Actions) | ✅ Operationeel | Auto-deploy naar Hetzner |
| AI issue triage | ✅ Operationeel | Claude Opus triage bot |
| SSL / HTTPS | ✅ Operationeel | Let's Encrypt via Certbot |
| Drupal data-migratie | 🔲 Ontbreekt | Blokkerende gap |
| CMS / configureerbaar menu | 🔲 Ontbreekt | Handmatige workaround |
| nl.internet.nl 100% | ⚠️ Onbekend | Niet gemeten in productie |
| Matomo activeren | ⚠️ Deels | Backend klaar, frontend niet |
| 2FA bypass gepatcht | 🔴 Openstaand | Security kwetsbaarheid |
| JWT httpOnly cookies | 🔴 Openstaand | Security kwetsbaarheid |
| Rate limiting | 🔴 Openstaand | Security gap |

### 6.2 Sterke punten

- **Volledige tech stack geïmplementeerd** — het fundament is solide en modern.
- **CI/CD is volwassen** — auto-deploy, AI triage, geautomatiseerde tests.
- **GEMMA-integratie aanwezig** — kernonderscheidend vermogen is er.
- **Open source door opzet** — EUPL-1.2, GitHub, transparant.
- **Alle EIS-issues gesloten** — 12/12 EIS-items geïmplementeerd.

### 6.3 Knelpunten

- **Security gaps zijn open in productie** — 2FA bypass en JWT-opslag zijn actieve risico's.
- **Geen adoptiedata** — Matomo staat niet aan, dus gebruiksinzicht ontbreekt volledig.
- **Drupal-migratie is ongedaan** — de oude catalogus kan niet worden afgeschakeld.
- **CMS ontbreekt** — functioneel beheerder kan teksten niet zelfstandig beheren.
- **Geen formele SLA of beheerovereenkomst** — governance is nog informeel.

### 6.4 Quick wins

| # | Quick win | Effort | Impact |
|---|---|---|---|
| QW1 | Matomo frontend activeren (#35) | Klein | Gebruiksinzicht direct |
| QW2 | OpenAPI schema endpoint live (#38) | Klein | API-consumers unblocked |
| QW3 | Rate limiting basisconfiguratie (#39) | Klein | Security direct verbeterd |
| QW4 | GEMMA-component filter (#50) | Gemiddeld | UX voor architecten |

### 6.5 Gap-prioritering

| Gap | Impact | Urgentie | Prioriteit |
|---|---|---|---|
| 2FA bypass open | Hoog | Kritiek | **P1** |
| JWT localStorage | Hoog | Kritiek | **P1** |
| Drupal-migratie ontbreekt | Hoog | Hoog | **P2** |
| Rate limiting ontbreekt | Gemiddeld | Hoog | **P2** |
| Matomo niet actief | Laag | Gemiddeld | **P3** |
| CMS ontbreekt | Gemiddeld | Gemiddeld | **P3** |
| nl.internet.nl ongemeten | Gemiddeld | Laag | **P4** |

---

## 7. Productvolwassenheid

### Volwassenheidsmodel (schaal 1–5)

| 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| Ad hoc / chaotisch | Herhaalbaar | Gedefinieerd | Gemeten | Optimaliserend |

### Beoordeling per dimensie

| Dimensie | Score | Toelichting |
|---|---|---|
| **Functionele volwassenheid** | 3/5 | Alle EIS geïmplementeerd; wensen en CMS ontbreken |
| **Technische volwassenheid** | 3/5 | Solide stack; security-gaps open; geen formele observability |
| **Datavolwassenheid** | 2/5 | Datamodel goed; geen echte data (pre-migratie); kwaliteitsprocessen ontbreken |
| **Procesvolwassenheid** | 3/5 | CI/CD mature; AI triage werkend; geen change advisory board |
| **Governance** | 2/5 | Eigenaarschap bij VNG-R formeel; geen SLA; geen besluitvormingsproces gedocumenteerd |
| **Adoptie** | 1/5 | Geen meting; waarschijnlijk nul echte gemeenten in productie |
| **Operationeel beheer** | 2/5 | Productie draait; geen monitoring dashboard; geen on-call rota |

**Gemiddeld: 2.3/5 — "Herhaalbaar naar Gedefinieerd"**

> Het platform heeft een sterk technisch fundament maar is operationeel en qua adoptie nog vroeg stadium. De grootste sprong naar niveau 3–4 zit in: governance formaliseren, adoptie starten, en observability inrichten.

---

## 8. Governance en eigenaarschap

### 8.1 Rolverdeling

| Rol | Persoon / Organisatie | Verantwoordelijkheid |
|---|---|---|
| **Product Owner** | VNG Realisatie BV | Prioriteiten roadmap; go/no-go releases |
| **Functioneel beheerder** | VNG Realisatie (team) | Operationeel beheer; gebruikerssupport; fiatteringen |
| **Technisch eigenaar** | Ontwikkelteam | Technische architectuur; security; CI/CD |
| **Datakwaliteitsverantwoordelijke** | VNG Realisatie | Actualiteitsborging; adoptie-KPI's |
| **Informatiebeveiligingsfunctionaris** | VNG Realisatie / IBD | Security baseline; BIO-compliance |

> **Aanname:** ⚠️ Bovenstaande rolverdeling is gebaseerd op de aanbestedingscontext. Formele functiebenamingen en personen zijn nog niet vastgelegd.

### 8.2 Besluitvorming over prioriteiten

Aanbevolen cadans:

| Overleg | Frequentie | Deelnemers | Doel |
|---|---|---|---|
| **Sprint review** | 2-wekelijks | PO + team | Geleverd werk reviewen; feedback ophalen |
| **Roadmap review** | Maandelijks | PO + stakeholders | Roadmap bijstellen op basis van adoptie en incidenten |
| **Stuurgroep** | Kwartaal | VNG-R MT + PO | Strategische keuzes; budget; go/no-go grote releases |
| **Security review** | Kwartaal | PO + IB-functionaris | CVE's, pentest-uitkomsten, BIO-compliance |

### 8.3 Wijzigingsproces

1. Issue aangemaakt met template (functioneel of technisch).
2. AI PM triage bot bepaalt prioriteit, type, fase en auto-implementeerbaarheid.
3. PO reviewt triage en accordeert of past bij.
4. Issues met label `auto:implement` worden opgepakt door Claude Code agent.
5. PR wordt gereviewd door minimaal één developer + PO-signoff voor EIS-wijzigingen.
6. Productiedeploy via geautomatiseerde CI/CD pipeline.

### 8.4 Kwaliteitsafwijkingen

- Kritieke bugs (P1/P2): directe escalatie naar PO; bugfix-release buiten sprint.
- Security vulnerabilities: directe patch; geen wachttijd op sprint.
- Datalekken: conform VNG incident response procedure; DPA-melding indien nodig.

---

## 9. Randvoorwaarden en afhankelijkheden

### 9.1 Kritieke afhankelijkheden (blokkeerbaar voor roadmap)

| Afhankelijkheid | Type | Status | Mitigatie bij uitblijven |
|---|---|---|---|
| Drupal database dump van VNG-R | Brondata | ⚠️ Onbevestigd | Handmatige CSV-export als fallback |
| Domeinnaam + DNS (DNSSEC/IPv6) | Infrastructuur | ⚠️ Onbevestigd | nl.internet.nl 100% niet haalbaar |
| Anthropic API key (triage bot) | Externe dienst | ✅ Aanwezig | Triage handmatig als fallback |
| SMTP provider (Sendgrid o.a.) | Externe dienst | ⚠️ Placeholder | Geen e-mailnotificaties |
| GEMMA Online API of AMEFF export | Architectuurdata | ⚠️ Aanname | Handmatige upload door functioneel beheerder |

### 9.2 Capaciteit en budget

> **Aanname:** ⚠️ Er is een ontwikkelteam beschikbaar (1–2 FTE) voor doorontwikkeling. Bij uitval of budgetkorting vertraagt de roadmap met minimaal één fase.

### 9.3 Architectuurkaders

- Haven-compatibiliteit (Kubernetes) is strategisch vereist maar niet blokkerend op korte termijn.
- EUPL-1.2 licentie is niet onderhandelbaar voor alle maatwerk.
- Data uitsluitend binnen EER — blokkerend voor cloud-keuzes.

### 9.4 Adoptievereisten

Zonder actieve onboarding-campagne zal adoptie uitblijven. Vereist:
- Communicatie aan alle gemeentesecretarissen / CIO's.
- Handleiding en videotutorial.
- Ondersteuning bij eerste registratie (helpdesk of buddy-systeem).

---

## 10. Risico's en mitigaties

| # | Risico | Impact | Kans | Prioriteit | Mitigatie |
|---|---|---|---|---|---|
| R1 | **Security exploit via open 2FA bypass** | Kritiek | Gemiddeld | 🔴 Kritiek | Patch direct (#5, #6); zie Fase A |
| R2 | **Lage adoptie gemeenten** | Hoog | Hoog | 🔴 Kritiek | Communicatiecampagne; onboarding ondersteuning; verplichte registratie als beleidsoptie |
| R3 | **Drupal-migratie mislukt of vertraagt** | Hoog | Gemiddeld | 🔴 Kritiek | Vroeg starten; dry-run mode; parallelle systemen tijdelijk |
| R4 | **Datadegradatie na launch** | Hoog | Hoog | 🟠 Hoog | Attendering bij verlopen data; datakwaliteitsproces; maandelijkse rapporten aan beheerders |
| R5 | **Vendor lock-in Hetzner / infra** | Gemiddeld | Laag | 🟡 Gemiddeld | Kubernetes-ready architectuur; Docker Compose als abstractie |
| R6 | **GEMMA-model wijzigt fundamenteel** | Hoog | Laag | 🟡 Gemiddeld | Versiemanagement GEMMA-import; backward compatible datamodel |
| R7 | **Anthropic API key verlopen / kostenexplosie** | Laag | Laag | 🟢 Laag | Fallback naar handmatige triage; kostenalarm instellen |
| R8 | **Capaciteitstekort ontwikkelteam** | Hoog | Gemiddeld | 🟠 Hoog | Prioriteer P1/P2 strikt; gebruik AI-agent voor routine-implementaties |
| R9 | **AVG-incident bij document sharing** | Hoog | Laag | 🟠 Hoog | Zichtbaarheidsinstellingen goed getest; DPA-melding procedure klaar |
| R10 | **Concurrent platform (eigen gemeente-tools)** | Gemiddeld | Gemiddeld | 🟡 Gemiddeld | Actief stakeholder management; unieke GEMMA-waardepropositie benadrukken |

---

## 11. Advies en besluitpunten

### 11.1 Belangrijkste conclusies

1. **Het technisch fundament is gereed** — alle MVP EIS-items zijn geïmplementeerd. Het platform kan productieklaar worden verklaard zodra de security-gaps zijn gedicht.

2. **Adoptie is het primaire risico** — een technisch goed platform zonder gebruikers heeft geen waarde. Dit vereist organisatorische actie van VNG Realisatie, niet alleen technische.

3. **Security is een blokkeerder** — de open 2FA bypass en JWT-localStorage kwetsbaarheden mogen niet in een productiesysteem blijven.

4. **Datakwaliteit is een continu proces** — zonder governance op actualiteit zal de catalogus binnen een jaar verouderen.

5. **Governance is informeel** — producteigenaarschap, SLA's en besluitvorming moeten formeel worden vastgelegd.

### 11.2 Aanbevolen prioriteiten (gesorteerd)

| Prioriteit | Actie | Tijdlijn |
|---|---|---|
| **1** | Patch security-gaps (#5, #6, #39) | Direct, week 1 |
| **2** | Drupal-migratie starten (data aanvragen bij VNG-R) | Week 2–4 |
| **3** | OpenAPI schema + Matomo activeren (#35, #38) | Week 2–3 |
| **4** | Governance formaliseren (PO, SLA, overlegstructuur) | Maand 1 |
| **5** | Onboarding campagne voorbereiden (top 10 gemeenten) | Maand 2 |
| **6** | nl.internet.nl 100% meting + actieplan | Maand 2 |
| **7** | Roadmap fase B uitvoeren | Q2 2026 |

### 11.3 Besluitpunten voor management / productsturing

> De volgende besluiten zijn vereist en kunnen niet door het ontwikkelteam worden genomen:

| # | Besluitpunt | Opties | Aanbeveling |
|---|---|---|---|
| B1 | **Formele SLA productie** | (a) Geen SLA (b) 99% (c) 99.5% | Start met 99%; schaal naar 99.5% bij Kubernetes |
| B2 | **Drupal afschakelmoment** | (a) Na succesvolle migratie (b) Vaste datum | Stel vaste datum (bijv. 1 juli 2026) als stok achter de deur |
| B3 | **Adoptieverplichting** | (a) Vrijwillig (b) Verplicht voor gemeenten die VNG-subsidie ontvangen | Aanbeveling: start vrijwillig met sterke campagne; evalueer na 6 maanden |
| B4 | **Kubernetes / Haven migratie timing** | (a) Nu (b) Na adoptie-plateau (c) Nooit | Wacht op 50% adoptie; focus eerst op inhoud |
| B5 | **Reviews en ratings (W2) moderatiebeleid** | (a) Anoniem (b) Geverifieerd account (c) Geen reviews | Alleen geverifieerde accounts; anonimiteit te gevoelig voor gemeentepolitiek |
| B6 | **AI-aanbevelingen (D1) tijdlijn** | (a) Zodra data beschikbaar (b) Pas na 1 jaar productiedata | Pas na 1 jaar; AI op dunne data is misleidend |

---

## Bijlage A — Issue overzicht per fase (huidige backlog)

| Issue | Titel | Fase | Prioriteit |
|---|---|---|---|
| #5 | 2FA bypass blokkeren | A | 🔴 Kritiek |
| #6 | JWT → httpOnly cookies | A | 🔴 Kritiek |
| #39 | Rate limiting | A | 🔴 Kritiek |
| #38 | OpenAPI schema endpoint | A | 🟠 Hoog |
| #37 | Frontend a11y tests | A | 🟠 Hoog |
| #35 | Matomo frontend activeren | A | 🟡 Gemiddeld |
| #34 | Configureerbaar menu | A | 🟡 Gemiddeld |
| #50 | GEMMA-component filter | B | 🟡 Gemiddeld |
| #33 | BIO beveiligingseisen | C | 🟠 Hoog |
| #32 | Reviews en ratings | C | 🟡 Gemiddeld |
| #31 | Koppelingendiagram | C | 🟡 Gemiddeld |
| #30 | Pakket vergelijken | C | 🟡 Gemiddeld |

---

*Document bijgehouden door: AI Product Manager (Claude Opus) + Product Owner VNG Realisatie*
*Bronnen: CLAUDE.md projectdocumentatie, aanbesteding TN492936, GitHub issue-analyse (maart 2026)*
*Volgende review: juni 2026*
