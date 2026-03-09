#!/usr/bin/env bash
# =============================================================================
# setup-server.sh — Eenmalige serverinstallatie voor Softwarecatalogus
# Uitvoeren als root op een verse Ubuntu 24.04 server
#
# Gebruik:
#   curl -fsSL https://raw.githubusercontent.com/.../setup-server.sh | bash
#   of: scp infra/scripts/setup-server.sh root@204.168.145.63: && ssh root@204.168.145.63 bash setup-server.sh
# =============================================================================
set -euo pipefail

# --- Configuratie -----------------------------------------------------------
APP_USER="swc"
APP_DIR="/opt/softwarecatalogus"
DOMAIN="${DOMAIN_NAME:-}"          # Optioneel: stel in voor SSL
GITHUB_REPO="${GITHUB_REPO:-}"     # Optioneel: bijv. org/softwarecatalogus

echo "=== Softwarecatalogus server setup ==="
echo "App user: $APP_USER"
echo "App dir:  $APP_DIR"

# --- Systeem update ---------------------------------------------------------
echo "[1/8] Systeem updaten..."
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq \
    git \
    curl \
    wget \
    unzip \
    ufw \
    fail2ban \
    htop \
    ca-certificates \
    gnupg \
    lsb-release

# --- Docker installatie -----------------------------------------------------
echo "[2/8] Docker installeren..."
if ! command -v docker &>/dev/null; then
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
        gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
        https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
        tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
    systemctl enable docker
    systemctl start docker
    echo "Docker geïnstalleerd: $(docker --version)"
else
    echo "Docker al geïnstalleerd: $(docker --version)"
fi

# --- Applicatiegebruiker aanmaken -------------------------------------------
echo "[3/8] Applicatiegebruiker aanmaken..."
if ! id "$APP_USER" &>/dev/null; then
    useradd -m -s /bin/bash "$APP_USER"
    usermod -aG docker "$APP_USER"
    echo "Gebruiker $APP_USER aangemaakt"
else
    echo "Gebruiker $APP_USER bestaat al"
fi

# Voeg ook huidige user toe aan docker groep
usermod -aG docker "${SUDO_USER:-root}" 2>/dev/null || true

# --- Applicatiemap aanmaken -------------------------------------------------
echo "[4/8] Applicatiemap aanmaken..."
mkdir -p "$APP_DIR"
chown "$APP_USER:$APP_USER" "$APP_DIR"

# --- Firewall instellen -----------------------------------------------------
echo "[5/8] Firewall instellen (UFW)..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
echo "UFW status:"
ufw status

# --- Fail2ban instellen -----------------------------------------------------
echo "[6/8] Fail2ban instellen..."
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
EOF
systemctl enable fail2ban
systemctl restart fail2ban

# --- SSH hardening -----------------------------------------------------------
echo "[7/8] SSH hardening..."
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
systemctl reload sshd
echo "SSH: wachtwoord-login uitgeschakeld, root-login alleen met key"

# --- Repository clonen (optioneel) ------------------------------------------
echo "[8/8] Repository opzetten..."
if [[ -n "$GITHUB_REPO" ]]; then
    if [[ ! -d "$APP_DIR/.git" ]]; then
        sudo -u "$APP_USER" git clone "https://github.com/$GITHUB_REPO.git" "$APP_DIR"
        echo "Repository gecloned: $GITHUB_REPO"
    else
        echo "Repository bestaat al in $APP_DIR"
    fi
else
    echo "GITHUB_REPO niet ingesteld — sla klonen over"
    echo "Clone handmatig met: git clone <repo-url> $APP_DIR"
fi

# --- Klaar ------------------------------------------------------------------
echo ""
echo "============================================"
echo " Setup voltooid!"
echo "============================================"
echo ""
echo "Volgende stappen:"
echo "1. Kopieer .env.production naar $APP_DIR/.env.production"
echo "   scp .env.production $APP_USER@$(hostname -I | awk '{print $1}'):$APP_DIR/"
echo ""
echo "2. Start de applicatie:"
echo "   ssh $APP_USER@$(hostname -I | awk '{print $1}')"
echo "   cd $APP_DIR && bash infra/scripts/deploy.sh"
echo ""
if [[ -n "$DOMAIN" ]]; then
    echo "3. SSL certificaat aanvragen:"
    echo "   bash infra/scripts/certbot-init.sh $DOMAIN admin@$DOMAIN"
fi
echo ""
echo "Server IP: $(hostname -I | awk '{print $1}')"
