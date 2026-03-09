#!/usr/bin/env bash
# ─── Demo Reset Script ──────────────────────────────────────────────────────────
# Herstelt de demo-startstand door de database te wissen en opnieuw te seeden.
# Gebruik ALTIJD dit script voordat je de "registratiestroom"-suite opneemt
# (scènes 17-20), zodat de TechSolutions BV-registratie een verse start heeft.
#
# Gebruik:
#   bash scripts/demo-reset.sh
#
# Vereisten:
#   - Docker Compose draait: docker compose ps
#   - Backend container heet 'backend' (zie docker-compose.yml)
# ───────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║       Softwarecatalogus — Demo Reset                  ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Ga naar projectroot zodat docker compose de juiste compose-file vindt
cd "$PROJECT_ROOT"

# Controleer of docker compose beschikbaar is
if ! docker compose version &>/dev/null; then
  echo "❌  docker compose niet gevonden. Installeer Docker Desktop en probeer opnieuw."
  exit 1
fi

# Controleer of de backend container draait
if ! docker compose ps --services --filter "status=running" | grep -q "backend"; then
  echo "❌  Backend container draait niet."
  echo "     Start eerst: docker compose up -d"
  exit 1
fi

echo "🔄  Demo-data wissen en opnieuw seeden..."
docker compose exec backend python manage.py seed_data --clear

echo ""
echo "✅  Demo-startstand hersteld!"
echo ""
echo "   Beschikbare accounts:"
echo "   ─────────────────────────────────────────────────────"
echo "   Admin (functioneel beheerder)"
echo "     E-mail:     admin@vngrealisatie.nl"
echo "     Wachtwoord: Welkom01!"
echo "   "
echo "   Gemeente Utrecht (gebruik-beheerder)"
echo "     E-mail:     j.jansen@utrecht.nl"
echo "     Wachtwoord: Welkom01!"
echo "   "
echo "   Centric (aanbod-beheerder)"
echo "     E-mail:     verkoop@centric.eu"
echo "     Wachtwoord: Welkom01!"
echo "   ─────────────────────────────────────────────────────"
echo "   Nieuw aan te maken tijdens demo (scène 17):"
echo "     E-mail:     pieter@techsolutions.nl"
echo "     Wachtwoord: Welkom12345!"
echo "   ─────────────────────────────────────────────────────"
echo ""
echo "🎬  Klaar voor demo-opname!"
echo "     Gebruik: cd demo && npx ts-node run-demo.ts --suite registratiestroom"
echo ""
