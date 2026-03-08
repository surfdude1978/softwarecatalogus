# ============================================================
# GitHub Labels en Issues aanmaken voor Softwarecatalogus
# ============================================================
# Vereist: GitHub CLI (gh) geinstalleerd en ingelogd
# Installeren: winget install --id GitHub.cli
# Inloggen:    gh auth login
# Uitvoeren:   .\scripts\github_setup.ps1
# ============================================================

$REPO = "surfdude1978/softwarecatalogus"
$TMPDIR = $env:TEMP

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
    $out = gh label create $label.name --color $label.color --description $label.description --repo $REPO 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        $out2 = gh label edit $label.name --color $label.color --description $label.description --repo $REPO 2>&1
        Write-Host " (bijgewerkt)" -ForegroundColor Gray
    }
}

Write-Host ""

# ── Hulpfunctie: issue aanmaken via tijdelijk bestand ──────

function New-Issue {
    param(
        [string]$Title,
        [string]$Body,
        [string]$Labels
    )
    $tmpFile = Join-Path $TMPDIR "gh_issue_body.md"
    [System.IO.File]::WriteAllText($tmpFile, $Body, [System.Text.Encoding]::UTF8)
    Write-Host "  Issue: $($Title.Substring(0, [Math]::Min(70, $Title.Length)))..." -NoNewline
    $out = gh issue create --title $Title --body-file $tmpFile --label $Labels --repo $REPO 2>&1
    Remove-Item $tmpFile -ErrorAction SilentlyContinue
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " FOUT: $out" -ForegroundColor Red
    }
}

# ── Issues ─────────────────────────────────────────────────

Write-Host "Issues aanmaken..." -ForegroundColor Yellow

New-Issue `
    -Title "[EIS] Audit logging - alle schrijfacties loggen" `
    -Labels "eis,security,ready-for-claude" `
    -Body "## Beschrijving`nAlle mutaties (aanmaken, bijwerken, verwijderen) moeten worden gelogd voor traceerbaarheid en compliance.`n`n## Acceptatiecriteria`n- [ ] AuditLog model aanmaken (actor, actie, object_type, object_id, tijdstip, IP-adres)`n- [ ] Mixin voor automatische logging op alle ModelViewSet acties`n- [ ] Leesbaar overzicht in Django Admin`n- [ ] Exporteerbaar als CSV door functioneel beheerder"

New-Issue `
    -Title "[EIS] Export functionaliteit - CSV, Excel en AMEFF" `
    -Labels "eis,enhancement,ready-for-claude" `
    -Body "## Beschrijving`nGebruik-beheerders moeten hun pakketlandschap kunnen exporteren als CSV, Excel en AMEFF (ArchiMate Exchange).`n`n## Acceptatiecriteria`n- [ ] GET /api/v1/export/pakketoverzicht.csv`n- [ ] GET /api/v1/export/pakketoverzicht.xlsx`n- [ ] GET /api/v1/export/pakketoverzicht.ameff`n- [ ] Download-knop in mijn-landschap dashboard`n- [ ] Auth: alleen eigen landschap"

New-Issue `
    -Title "[EIS] WCAG 2.1 AA - toegankelijkheidsaudit en fixes" `
    -Labels "eis,accessibility,ready-for-claude" `
    -Body "## Beschrijving`nHet platform moet voldoen aan WCAG 2.1 AA (digitoegankelijk.nl standaard).`n`n## Acceptatiecriteria`n- [ ] axe-core of Lighthouse CI in CI/CD`n- [ ] Alle formulieren hebben correcte labels en foutmeldingen`n- [ ] Kleurcontrast minimaal 4.5:1 voor normale tekst`n- [ ] Toetsenbordnavigatie volledig functioneel`n- [ ] Skip-to-content link aanwezig`n- [ ] ARIA-attributen correct op alle interactieve elementen"

New-Issue `
    -Title "[EIS] Test coverage minimaal 80% - backend unit en integratie tests" `
    -Labels "eis,tests,ready-for-claude" `
    -Body "## Beschrijving`nMinimaal 80% code coverage vereist voor productieomgeving.`n`n## Acceptatiecriteria`n- [ ] pytest-cov instellen in CI`n- [ ] Tests voor alle ViewSet acties (CRUD + permissies)`n- [ ] Tests voor TenderNed sync task (mock externe API)`n- [ ] Tests voor exportfunctionaliteit`n- [ ] Tests voor authenticatie (login, 2FA, token refresh)`n- [ ] Coverage report in CI/CD pipeline"

New-Issue `
    -Title "[EIS] GEMMA architectuurkaart - visuele weergave pakketlandschap" `
    -Labels "eis,gemma,enhancement,ready-for-claude" `
    -Body "## Beschrijving`nInteractieve weergave van GEMMA-referentiearchitectuur kaart met pakketten geplot op componenten.`n`n## Acceptatiecriteria`n- [ ] SVG-gebaseerde GEMMA kaart component`n- [ ] Pakketten geplot op bijbehorende GEMMA-component`n- [ ] Kleurcodering: in gebruik (groen) / gepland (oranje) / verouderd (grijs)`n- [ ] Zoom en pan functionaliteit`n- [ ] Klikken op pakket opent detailpagina`n- [ ] Export als PNG/PDF"

New-Issue `
    -Title "[EIS] Zelfregistratie organisaties - fiatteerstroom" `
    -Labels "eis,enhancement,ready-for-claude" `
    -Body "## Beschrijving`nLeveranciers en gemeenten moeten zichzelf kunnen registreren. Concept-status totdat functioneel beheerder fiatteert.`n`n## Acceptatiecriteria`n- [ ] Registratieformulier voor nieuwe organisatie en eerste gebruiker`n- [ ] E-mailbevestiging na registratie`n- [ ] Notificatie naar functioneel beheerder bij nieuwe concept-organisatie`n- [ ] Fiatteringspagina in beheer-dashboard`n- [ ] Na fiattering: welkomstmail en TOTP setup flow"

New-Issue `
    -Title "[WENS] TenderNed productie-modus - echte API koppeling" `
    -Labels "wens,tenderned,ready-for-claude" `
    -Body "## Beschrijving`nDe huidige TenderNed integratie gebruikt demo-data. Voor productie moet de echte TenderNed Open Data API worden aangekoppeld.`n`n## Acceptatiecriteria`n- [ ] TENDERNED_DEMO_MODE=False werkt in productie`n- [ ] Foutafhandeling bij API-uitval (retry, graceful degradation)`n- [ ] Rate limiting respecteren`n- [ ] Monitoring: alert bij mislukte dagelijkse sync"

New-Issue `
    -Title "[WENS] nl.internet.nl 100% score - security headers productie" `
    -Labels "wens,security,ready-for-claude" `
    -Body "## Beschrijving`nHet platform moet 100% scoren op nl.internet.nl voor HTTPS/TLS, DNSSEC, DKIM+DMARC, IPv6 en beveiligingsheaders.`n`n## Acceptatiecriteria`n- [ ] HSTS header (Strict-Transport-Security)`n- [ ] Content Security Policy (CSP) headers`n- [ ] DNSSEC geconfigureerd op domein`n- [ ] DKIM + DMARC voor e-mail`n- [ ] IPv6 ondersteuning`n- [ ] TLS 1.3 minimum"

Write-Host ""
Write-Host "=== Klaar! ===" -ForegroundColor Green
Write-Host "Bekijk de issues op: https://github.com/$REPO/issues" -ForegroundColor Cyan
