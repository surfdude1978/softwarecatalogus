#!/usr/bin/env bash
# =============================================================================
# deploy.sh — Deploy/update Softwarecatalogus op de productieserver
#
# Gebruik (lokaal, via SSH):
#   ssh swc@204.168.145.63 "cd /opt/softwarecatalogus && bash infra/scripts/deploy.sh"
#
# Of direct:
#   bash infra/scripts/deploy.sh
# =============================================================================
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/softwarecatalogus}"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"
MAX_RETRIES=4

cd "$APP_DIR"

echo "=== Softwarecatalogus deploy $(date '+%Y-%m-%d %H:%M:%S') ==="

# --- Controleer vereisten ---------------------------------------------------
if [[ ! -f "$ENV_FILE" ]]; then
    echo "FOUT: $ENV_FILE niet gevonden in $APP_DIR"
    echo "Maak eerst .env.production aan op basis van .env.production.example"
    exit 1
fi

# --- Git pull met retry ------------------------------------------------------
echo "[1/5] Code updaten..."
RETRY=0
until git pull origin master 2>/dev/null || git pull origin main 2>/dev/null; do
    RETRY=$((RETRY + 1))
    if [[ $RETRY -ge $MAX_RETRIES ]]; then
        echo "FOUT: git pull mislukt na $MAX_RETRIES pogingen"
        exit 1
    fi
    WAIT=$((2 ** RETRY))
    echo "git pull mislukt, opnieuw proberen in ${WAIT}s..."
    sleep "$WAIT"
done
echo "Code geupdate: $(git log -1 --format='%h %s')"

# --- Docker images bouwen ----------------------------------------------------
echo "[2/5] Docker images bouwen..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --pull

# --- Migraties uitvoeren (vóór container swap) --------------------------------
echo "[3/5] Database migraties uitvoeren..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" run --rm backend \
    python manage.py migrate --noinput

# --- Containers opnieuw starten (zero-downtime via rolling update) -----------
echo "[4/5] Containers starten..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --remove-orphans

# --- Meilisearch index bijwerken --------------------------------------------
echo "[5/5] Zoekindex bijwerken..."
sleep 5  # Wacht tot backend gestart is
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T backend \
    python manage.py search_index --rebuild -f 2>/dev/null || \
    echo "Zoekindex update overgeslagen (command niet beschikbaar)"

# --- Opruimen ---------------------------------------------------------------
docker image prune -f --filter "until=168h" 2>/dev/null || true

# --- Status tonen -----------------------------------------------------------
echo ""
echo "=== Status ==="
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
echo ""
echo "Deploy voltooid: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Commit: $(git log -1 --format='%h — %s (%an)')"
