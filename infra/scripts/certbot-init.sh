#!/usr/bin/env bash
# =============================================================================
# certbot-init.sh — Eerste SSL-certificaat aanvragen via Let's Encrypt
#
# Gebruik:
#   bash infra/scripts/certbot-init.sh softwarecatalogus.example.nl admin@example.nl
#
# Vereisten:
#   - Domeinnaam verwijst al naar dit IP (DNS A-record)
#   - Nginx draait al op poort 80 (voor ACME challenge)
# =============================================================================
set -euo pipefail

DOMAIN="${1:?Gebruik: $0 <domein> <email>}"
EMAIL="${2:?Gebruik: $0 <domein> <email>}"
APP_DIR="${APP_DIR:-/opt/softwarecatalogus}"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"

cd "$APP_DIR"

echo "=== SSL certificaat aanvragen voor $DOMAIN ==="

# Stap 1: Tijdelijke HTTP-only nginx starten (zonder SSL redirect)
echo "[1/3] Nginx starten voor ACME challenge..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d nginx

# Stap 2: Certbot uitvoeren
echo "[2/3] Certificaat aanvragen..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" run --rm certbot \
    certbot certonly \
    --webroot \
    --webroot-path /var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

# Stap 3: Nginx herstarten met SSL
echo "[3/3] Nginx herstarten met SSL..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" restart nginx

echo ""
echo "Certificaat aangevraagd voor: $DOMAIN"
echo "Verloopdatum: $(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" run --rm certbot certbot certificates 2>/dev/null | grep 'Expiry Date' | head -1 || echo 'zie: certbot certificates')"
echo ""
echo "Automatische verlenging via certbot container actief (elke 12 uur)"
