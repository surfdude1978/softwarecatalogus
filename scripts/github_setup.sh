#!/bin/bash
# ============================================================
# GitHub Labels en Issues aanmaken via REST API
# Gebruik: GITHUB_TOKEN=ghp_xxx bash scripts/github_setup.sh
# ============================================================

REPO="surfdude1978/softwarecatalogus"
API="https://api.github.com"

if [ -z "$GITHUB_TOKEN" ]; then
  echo "FOUT: Stel GITHUB_TOKEN in:"
  echo "  export GITHUB_TOKEN=ghp_JOUWTOKEN"
  echo "  bash scripts/github_setup.sh"
  exit 1
fi

AUTH="Authorization: Bearer $GITHUB_TOKEN"
ACCEPT="Accept: application/vnd.github+json"
CT="Content-Type: application/json"

# Test verbinding
echo "=== Verbinding testen ==="
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" -H "$ACCEPT" "$API/repos/$REPO")
if [ "$STATUS" != "200" ]; then
  echo "FOUT: Kan repo niet bereiken (HTTP $STATUS). Controleer token en repo-naam."
  exit 1
fi
echo "Verbinding OK - repo: $REPO"
echo ""

# ── Label aanmaken ──────────────────────────────────────────

make_label() {
  local name="$1" color="$2" desc="$3"
  local body="{\"name\":\"$name\",\"color\":\"$color\",\"description\":\"$desc\"}"
  local code=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST -H "$AUTH" -H "$ACCEPT" -H "$CT" \
    -d "$body" "$API/repos/$REPO/labels")
  if [ "$code" = "201" ]; then
    echo "  + $name"
  elif [ "$code" = "422" ]; then
    # Al aanwezig, update
    local encoded=$(echo -n "$name" | sed 's/ /%20/g' | sed 's/#/%23/g')
    curl -s -o /dev/null -X PATCH -H "$AUTH" -H "$ACCEPT" -H "$CT" \
      -d "$body" "$API/repos/$REPO/labels/$encoded"
    echo "  ~ $name (al aanwezig, bijgewerkt)"
  else
    echo "  ! $name (HTTP $code)"
  fi
}

echo "=== Labels aanmaken ==="
make_label "ready-for-claude"  "7B61FF" "Klaar om door Claude Code te worden opgepakt"
make_label "in-review"         "0075ca" "PR aangemaakt, wacht op review"
make_label "bug"               "d73a4a" "Er klopt iets niet"
make_label "enhancement"       "a2eeef" "Nieuwe functionaliteit of verbetering"
make_label "security"          "e4e669" "Beveiligingsgerelateerd"
make_label "accessibility"     "bfd4f2" "WCAG 2.1 AA toegankelijkheid"
make_label "performance"       "f9d0c4" "Performance verbetering"
make_label "tests"             "c5def5" "Tests schrijven of verbeteren"
make_label "tech-debt"         "e4e4e4" "Technische schuld oplossen"
make_label "eis"               "0e8a16" "Functionele eis (verplicht MVP)"
make_label "wens"              "fbca04" "Functionele wens (nice-to-have)"
make_label "gemma"             "1d76db" "GEMMA/ArchiMate gerelateerd"
make_label "tenderned"         "5319e7" "TenderNed integratie"
echo ""

# ── Issue aanmaken ──────────────────────────────────────────

make_issue() {
  local title="$1" body="$2" labels="$3"
  # Bouw labels JSON array (kommagescheiden naar ["a","b","c"])
  local labels_arr=$(echo "$labels" | sed 's/,/","/g' | sed 's/^/"/' | sed 's/$/"/')
  local safe_title=$(echo "$title" | sed 's/"/\\"/g')
  local safe_body=$(echo "$body" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')
  local data="{\"title\":\"$safe_title\",\"body\":\"$safe_body\",\"labels\":[$labels_arr]}"
  local code=$(curl -s -o /tmp/gh_resp.json -w "%{http_code}" \
    -X POST -H "$AUTH" -H "$ACCEPT" -H "$CT" \
    -d "$data" "$API/repos/$REPO/issues")
  if [ "$code" = "201" ]; then
    local num=$(grep -o '"number":[0-9]*' /tmp/gh_resp.json | head -1 | grep -o '[0-9]*')
    echo "  + #$num: $title"
  else
    echo "  ! Fout (HTTP $code): $title"
  fi
}

echo "=== Issues aanmaken ==="

make_issue \
  "[EIS] Audit logging - alle schrijfacties loggen" \
  "## Beschrijving\nAlle mutaties moeten worden gelogd voor traceerbaarheid en compliance.\n\n## Acceptatiecriteria\n- [ ] AuditLog model (actor, actie, object_type, object_id, tijdstip, IP)\n- [ ] AuditLogMixin voor automatische logging op alle ViewSet schrijfacties\n- [ ] Leesbaar overzicht in Django Admin\n- [ ] Exporteerbaar als CSV door functioneel beheerder" \
  "eis,security,ready-for-claude"

make_issue \
  "[EIS] Export functionaliteit - CSV, Excel en AMEFF" \
  "## Beschrijving\nGebruik-beheerders moeten hun pakketlandschap kunnen exporteren.\n\n## Acceptatiecriteria\n- [ ] GET /api/v1/export/pakketoverzicht.csv\n- [ ] GET /api/v1/export/pakketoverzicht.xlsx\n- [ ] GET /api/v1/export/pakketoverzicht.ameff\n- [ ] Download-knoppen in mijn-landschap dashboard\n- [ ] Auth: alleen eigen landschap" \
  "eis,enhancement,ready-for-claude"

make_issue \
  "[EIS] WCAG 2.1 AA - toegankelijkheidsaudit en fixes" \
  "## Beschrijving\nHet platform moet voldoen aan WCAG 2.1 AA (digitoegankelijk.nl).\n\n## Acceptatiecriteria\n- [ ] axe-core of Lighthouse CI in CI/CD\n- [ ] Correcte labels en foutmeldingen op alle formulieren\n- [ ] Kleurcontrast minimaal 4.5:1\n- [ ] Toetsenbordnavigatie volledig functioneel\n- [ ] Skip-to-content link aanwezig\n- [ ] ARIA-attributen correct op alle interactieve elementen" \
  "eis,accessibility,ready-for-claude"

make_issue \
  "[EIS] Test coverage minimaal 80% - backend tests" \
  "## Beschrijving\nMinimaal 80% code coverage voor productieomgeving.\n\n## Acceptatiecriteria\n- [ ] pytest-cov in CI\n- [ ] Tests voor alle ViewSet acties (CRUD + permissies)\n- [ ] Tests voor TenderNed sync (mock API)\n- [ ] Tests voor export en authenticatie\n- [ ] Coverage report in CI/CD pipeline" \
  "eis,tests,ready-for-claude"

make_issue \
  "[EIS] GEMMA architectuurkaart - visuele weergave pakketlandschap" \
  "## Beschrijving\nInteractieve GEMMA-kaart met pakketten geplot op componenten.\n\n## Acceptatiecriteria\n- [ ] SVG-gebaseerde GEMMA kaart component\n- [ ] Pakketten geplot op bijbehorende GEMMA-component\n- [ ] Kleurcodering: in gebruik / gepland / verouderd\n- [ ] Zoom en pan functionaliteit\n- [ ] Klikken op pakket opent detailpagina\n- [ ] Export als PNG/PDF" \
  "eis,gemma,enhancement,ready-for-claude"

make_issue \
  "[EIS] Zelfregistratie organisaties - fiatteerstroom" \
  "## Beschrijving\nLeveranciers en gemeenten registreren zichzelf. Concept-status tot functioneel beheerder fiatteert.\n\n## Acceptatiecriteria\n- [ ] Registratieformulier voor nieuwe organisatie en eerste gebruiker\n- [ ] E-mailbevestiging na registratie\n- [ ] Notificatie naar functioneel beheerder bij concept-organisatie\n- [ ] Fiatteringspagina in beheer-dashboard\n- [ ] Na fiattering: welkomstmail en TOTP setup flow" \
  "eis,enhancement,ready-for-claude"

make_issue \
  "[WENS] TenderNed productie-modus - echte API koppeling" \
  "## Beschrijving\nDe huidige TenderNed integratie gebruikt demo-data. Productie vereist echte API.\n\n## Acceptatiecriteria\n- [ ] TENDERNED_DEMO_MODE=False werkt in productie\n- [ ] Foutafhandeling bij API-uitval (retry, graceful degradation)\n- [ ] Rate limiting respecteren\n- [ ] Monitoring: alert bij mislukte dagelijkse sync" \
  "wens,tenderned,ready-for-claude"

make_issue \
  "[WENS] nl.internet.nl 100% score - security headers" \
  "## Beschrijving\n100% score op nl.internet.nl voor HTTPS, DNSSEC, DKIM+DMARC, IPv6 en beveiligingsheaders.\n\n## Acceptatiecriteria\n- [ ] HSTS header\n- [ ] Content Security Policy (CSP)\n- [ ] DNSSEC geconfigureerd\n- [ ] DKIM + DMARC voor e-mail\n- [ ] IPv6 ondersteuning\n- [ ] TLS 1.3 minimum" \
  "wens,security,ready-for-claude"

echo ""
echo "=== Klaar! ==="
echo "Bekijk: https://github.com/$REPO/issues"
