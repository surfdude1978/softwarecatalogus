# ============================================================
# GitHub Labels en Issues aanmaken voor Softwarecatalogus
# ============================================================
# Vereist: GitHub CLI (gh) geïnstalleerd en ingelogd
# Installeren: winget install --id GitHub.cli
# Inloggen:    gh auth login
# Uitvoeren:   .\scripts\github_setup.ps1
# ============================================================

$REPO = "surfdude1978/softwarecatalogus"

Write-Host "=== GitHub Setup: Softwarecatalogus ===" -ForegroundColor Cyan
Write-Host "Repository: $REPO" -ForegroundColor Gray
Write-Host ""

# ── Labels ─────────────────────────────────────────────────

Write-Host "Labels aanmaken..." -ForegroundColor Yellow

$labels = @(
    @{ name = "ready-for-claude";  color = "7B61FF"; description = "Klaar om door Claude Code te worden opgepakt" },
    @{ name = "in-review";         color = "0075ca"; description = "PR aangemaakt, wacht op review" },
    @{ name = "bug";               color = "d73a4a"; description = "Er klopt iets niet" },
    @{ name = "enhancement";       color = "a2eeef"; description = "Nieuwe functionaliteit of verbetering" },
    @{ name = "security";          color = "e4e669"; description = "Beveiligingsgerelateerd" },
    @{ name = "accessibility";     color = "bfd4f2"; description = "WCAG 2.1 AA toegankelijkheid" },
    @{ name = "performance";       color = "f9d0c4"; description = "Performance verbetering" },
    @{ name = "tests";             color = "c5def5"; description = "Tests schrijven of verbeteren" },
    @{ name = "tech-debt";         color = "e4e4e4"; description = "Technische schuld oplossen" },
    @{ name = "eis";               color = "0e8a16"; description = "Functionele eis (verplicht MVP)" },
    @{ name = "wens";              color = "fbca04"; description = "Functionele wens (nice-to-have)" },
    @{ name = "gemma";             color = "1d76db"; description = "GEMMA/ArchiMate gerelateerd" },
    @{ name = "tenderned";         color = "5319e7"; description = "TenderNed integratie" }
)

foreach ($label in $labels) {
    Write-Host "  Label: $($label.name)" -NoNewline
    $result = gh label create $label.name `
        --color $label.color `
        --description $label.description `
        --repo $REPO 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✓" -ForegroundColor Green
    } else {
        # Probeer te updaten als al bestaat
        $result = gh label edit $label.name `
            --color $label.color `
            --description $label.description `
            --repo $REPO 2>&1
        Write-Host " (bijgewerkt)" -ForegroundColor Gray
    }
}

Write-Host ""

# ── Issues ─────────────────────────────────────────────────

Write-Host "Issues aanmaken..." -ForegroundColor Yellow

$issues = @(
    @{
        title = "[EIS] Audit logging — alle schrijfacties loggen"
        body = @"
## Beschrijving
Alle mutaties (aanmaken, bijwerken, verwijderen) van pakketten, organisaties en gebruikers moeten worden gelogd voor traceerbaarheid en compliance.

## Acceptatiecriteria
- [ ] AuditLog model aanmaken (actor, actie, object_type, object_id, tijdstip, IP-adres)
- [ ] Django signal of mixin voor automatische logging op alle ModelViewSet acties
- [ ] Leesbaar overzicht in Django Admin
- [ ] Exporteerbaar als CSV door functioneel beheerder

## Labels
eis, security, ready-for-claude
"@
        labels = "eis,security,ready-for-claude"
    },
    @{
        title = "[EIS] Export functionaliteit — CSV, Excel en AMEFF"
        body = @"
## Beschrijving
Gebruik-beheerders moeten hun pakketlandschap kunnen exporteren als CSV, Excel (.xlsx) en AMEFF (ArchiMate Exchange).

## Acceptatiecriteria
- [ ] `GET /api/v1/export/pakketoverzicht.csv` endpoint
- [ ] `GET /api/v1/export/pakketoverzicht.xlsx` endpoint (openpyxl)
- [ ] `GET /api/v1/export/pakketoverzicht.ameff` endpoint (XML/ArchiMate)
- [ ] Download-knop in mijn-landschap dashboard
- [ ] Auth: alleen eigen landschap (gebruik-beheerder)

## Labels
eis, enhancement, ready-for-claude
"@
        labels = "eis,enhancement,ready-for-claude"
    },
    @{
        title = "[EIS] WCAG 2.1 AA — toegankelijkheidsaudit en fixes"
        body = @"
## Beschrijving
Het platform moet voldoen aan WCAG 2.1 AA (digitoegankelijk.nl standaard).

## Acceptatiecriteria
- [ ] axe-core of Lighthouse CI integreren in CI/CD
- [ ] Alle formulieren hebben correcte labels en foutmeldingen
- [ ] Kleurcontrast ≥ 4.5:1 voor normale tekst
- [ ] Toetsenbordnavigatie volledig functioneel (geen toetsenbordvallen)
- [ ] Skip-to-content link aanwezig
- [ ] Focus management bij modale dialogen
- [ ] ARIA-attributen correct op alle interactieve elementen

## Labels
eis,accessibility,ready-for-claude
"@
        labels = "eis,accessibility,ready-for-claude"
    },
    @{
        title = "[EIS] Test coverage ≥ 80% — backend unit en integratie tests"
        body = @"
## Beschrijving
Minimaal 80% code coverage vereist voor productieomgeving.

## Acceptatiecriteria
- [ ] pytest-cov instellen in CI
- [ ] Tests voor alle ViewSet acties (CRUD + permissies)
- [ ] Tests voor TenderNed sync task (mock externe API)
- [ ] Tests voor exportfunctionaliteit
- [ ] Tests voor authenticatie (login, 2FA, token refresh)
- [ ] Coverage report in CI/CD pipeline

## Labels
eis,tests,ready-for-claude
"@
        labels = "eis,tests,ready-for-claude"
    },
    @{
        title = "[EIS] GEMMA architectuurkaart — visuele weergave pakketlandschap"
        body = @"
## Beschrijving
Interactieve weergave van GEMMA-referentiearchitectuur kaart met pakketten geplot op componenten.

## Acceptatiecriteria
- [ ] SVG-gebaseerde GEMMA kaart component
- [ ] Pakketten geplot op bijbehorende GEMMA-component
- [ ] Kleurcodering: in gebruik (groen) / gepland (oranje) / verouderd (grijs)
- [ ] Zoom en pan functionaliteit
- [ ] Klikken op pakket → detailpagina
- [ ] Export als PNG/PDF

## Labels
eis,gemma,enhancement,ready-for-claude
"@
        labels = "eis,gemma,enhancement,ready-for-claude"
    },
    @{
        title = "[EIS] Zelfregistratie organisaties — fiatteerstroom"
        body = @"
## Beschrijving
Leveranciers en gemeenten moeten zichzelf kunnen registreren. De registratie heeft concept-status totdat een functioneel beheerder fiatteert.

## Acceptatiecriteria
- [ ] Registratieformulier voor nieuwe organisatie + eerste gebruiker
- [ ] E-mailbevestiging na registratie
- [ ] Functioneel beheerder ontvangt notificatie bij nieuwe concept-organisatie
- [ ] Fiatteringspagina in beheer-dashboard
- [ ] Na fiattering: welkomstmail + TOTP setup flow

## Labels
eis,enhancement,ready-for-claude
"@
        labels = "eis,enhancement,ready-for-claude"
    },
    @{
        title = "[WENS] TenderNed productie-modus — echte API koppeling"
        body = @"
## Beschrijving
De huidige TenderNed integratie gebruikt demo-data. Voor productie moet de echte TenderNed Open Data API worden aangekoppeld.

## Acceptatiecriteria
- [ ] `TENDERNED_DEMO_MODE=False` werkt in productie
- [ ] Echte TenderNed API URL geconfigureerd
- [ ] Foutafhandeling bij API-uitval (retry, graceful degradation)
- [ ] Rate limiting respecteren (TenderNed API-limieten)
- [ ] Monitoring: alert bij mislukte dagelijkse sync

## Labels
wens,tenderned,ready-for-claude
"@
        labels = "wens,tenderned,ready-for-claude"
    },
    @{
        title = "[WENS] nl.internet.nl 100% score — security headers productie"
        body = @"
## Beschrijving
Het platform moet 100% scoren op nl.internet.nl voor HTTPS/TLS, DNSSEC, DKIM+DMARC, IPv6 en beveiligingsheaders.

## Acceptatiecriteria
- [ ] HSTS header (Strict-Transport-Security)
- [ ] Content Security Policy (CSP) headers
- [ ] DNSSEC geconfigureerd op domein
- [ ] DKIM + DMARC voor e-mail
- [ ] IPv6 ondersteuning
- [ ] TLS 1.3 minimum

## Labels
wens,security,ready-for-claude
"@
        labels = "wens,security,ready-for-claude"
    }
)

foreach ($issue in $issues) {
    Write-Host "  Issue: $($issue.title.Substring(0, [Math]::Min(60, $issue.title.Length)))..." -NoNewline
    $result = gh issue create `
        --title $issue.title `
        --body $issue.body `
        --label $issue.labels `
        --repo $REPO 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✓" -ForegroundColor Green
    } else {
        Write-Host " ✗ ($result)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Klaar! ===" -ForegroundColor Green
Write-Host "Bekijk de issues op: https://github.com/$REPO/issues" -ForegroundColor Cyan
