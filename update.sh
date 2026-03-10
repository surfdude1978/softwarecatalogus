#!/bin/bash
set -e

echo "🔄 Ophalen laatste wijzigingen..."
git checkout main
git pull origin main

echo "✅ Klaar! Backend en frontend herladen automatisch."
echo "   Wacht even totdat Next.js de pagina ververst in je browser."
