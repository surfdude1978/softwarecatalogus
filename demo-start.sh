#!/usr/bin/env bash
# =============================================================================
# Softwarecatalogus — Demo omgeving starten
# =============================================================================
# Gebruik: ./demo-start.sh [--reset]
#
# --reset   Verwijder alle bestaande data en begin opnieuw
# =============================================================================

set -e
RESET=false
if [[ "$1" == "--reset" ]]; then
  RESET=true
fi

cd "$(dirname "$0")"

echo "======================================"
echo "  Softwarecatalogus — Demo opstarten"
echo "======================================"
echo ""

# Controleer vereisten
if ! command -v docker &>/dev/null; then
  echo "FOUT: Docker is niet geïnstalleerd." && exit 1
fi
if ! docker compose version &>/dev/null; then
  echo "FOUT: Docker Compose v2 is niet geïnstalleerd." && exit 1
fi

# Reset indien gevraagd
if $RESET; then
  echo "⚠  Reset: alle data en volumes worden verwijderd..."
  docker compose down -v --remove-orphans 2>/dev/null || true
  echo ""
fi

# Bouw en start alle services
echo "▶  Services bouwen en starten..."
docker compose up -d --build

echo ""
echo "⏳  Wachten tot de backend klaar is met opstarten"
echo "   (migrate → seed_data → sync_aanbestedingen → reindex_search)"
echo ""

# Wacht op de backend — klaar zodra runserver start
timeout=180
elapsed=0
while ! curl -sf http://localhost:8000/api/v1/pakketten/ >/dev/null 2>&1; do
  if [ $elapsed -ge $timeout ]; then
    echo ""
    echo "TIMEOUT: backend is na ${timeout}s nog niet bereikbaar."
    echo "Bekijk de logs met: docker compose logs backend"
    exit 1
  fi
  printf "."
  sleep 3
  elapsed=$((elapsed + 3))
done

echo ""
echo ""
echo "======================================"
echo "  ✅  Demo omgeving is klaar!"
echo "======================================"
echo ""
echo "  Frontend:   http://localhost:3000"
echo "  Backend API: http://localhost:8000/api/v1/"
echo "  Django admin: http://localhost:8000/admin/"
echo "  Nginx (aanbevolen): http://localhost:80"
echo ""
echo "  Inloggegevens (wachtwoord overal: Welkom01!)"
echo "  ─────────────────────────────────────────────"
echo "  Functioneel beheerder (VNG):"
echo "    admin@vngrealisatie.nl"
echo ""
echo "  Gebruik-beheerders (gemeenten):"
echo "    j.jansen@utrecht.nl        (Gemeente Utrecht)"
echo "    m.bakker@amsterdam.nl      (Gemeente Amsterdam)"
echo "    p.devries@rotterdam.nl     (Gemeente Rotterdam)"
echo "    s.meijer@denhaag.nl        (Gemeente Den Haag)"
echo "    r.degraaf@eindhoven.nl     (Gemeente Eindhoven)"
echo ""
echo "  Aanbod-beheerders (leveranciers):"
echo "    verkoop@centric.eu         (Centric)"
echo "    sales@pinkroccade.nl       (PinkRoccade)"
echo "    info@decos.com             (Decos)"
echo ""
echo "  Wachtende gebruiker (nog niet gefiateerd):"
echo "    nieuw@leverancier.nl"
echo ""
echo "  Logs bekijken:  docker compose logs -f backend"
echo "  Stoppen:        docker compose down"
echo "  Volledige reset: ./demo-start.sh --reset"
echo ""
