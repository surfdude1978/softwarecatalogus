# Demo-runner met Playwright + Chromium
# Draait de demo-opname geïsoleerd in Docker
#
# Build:  docker build -t swc-demo .
# Run:    docker run --rm --network host -v "%cd%\output:/demo/output" swc-demo
#
# Let op: --network host zodat de container http://localhost bereikt (de app).
# Op macOS gebruik: --add-host host.docker.internal:host-gateway
# en zet BASE_URL=http://host.docker.internal in de omgeving.

FROM mcr.microsoft.com/playwright:v1.58.2-jammy

WORKDIR /demo

# Kopieer projectbestanden
COPY package.json tsconfig.json ./
COPY helpers/ ./helpers/
COPY scenes/  ./scenes/
COPY run-demo.ts setup-auth.ts ./

# Installeer dependencies
RUN npm install

# Op Windows: bereik de host-app via host.docker.internal
ENV DEMO_BASE_URL=http://host.docker.internal

# Standaard: volledige demo opnemen
CMD ["npx", "ts-node", "run-demo.ts"]
