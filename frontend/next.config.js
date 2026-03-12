/** @type {import('next').NextConfig} */

const { execSync } = require("child_process");

// Haal de huidige git commit hash op bij build-tijd.
// Valt terug op de COMMIT_SHA omgevingsvariabele (CI/CD) of "onbekend".
function getCommitSha() {
  if (process.env.COMMIT_SHA) return process.env.COMMIT_SHA;
  try {
    return execSync("git rev-parse --short HEAD").toString().trim();
  } catch {
    return "onbekend";
  }
}

const COMMIT_SHA = getCommitSha();

// Build-timestamp in dd-mm-yyyy hh:mm formaat (Nederlandse tijdzone)
function getBuildTimestamp() {
  const now = new Date();
  const fmt = new Intl.DateTimeFormat("nl-NL", {
    timeZone: "Europe/Amsterdam",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
  return fmt.format(now);
}

const BUILD_TIMESTAMP = getBuildTimestamp();

const isDev = process.env.NODE_ENV === "development";

// Content Security Policy — strenger in productie, ruimer in development.
//
// Productie (nl.internet.nl vereiste):
//   • Geen unsafe-eval (verboden door OWASP/nl.internet.nl)
//   • connect-src beperkt tot self + wss + https
//   • upgrade-insecure-requests actief
//
// Development:
//   • unsafe-eval: vereist door Next.js webpack HMR en React Fast Refresh
//   • connect-src: sta ook http://localhost:8000 toe (directe backend-calls)
//   • ws:: WebSocket hot-reload op elk localhost-port
//   • Geen upgrade-insecure-requests (breekt http-dev-omgeving)
const CSP = [
  "default-src 'self'",
  isDev
    ? "script-src 'self' 'unsafe-inline' 'unsafe-eval'"
    : "script-src 'self' 'unsafe-inline'",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob: https:",
  "font-src 'self' data:",
  isDev
    ? "connect-src 'self' ws: wss: http://localhost:8000 https:"
    : "connect-src 'self' wss: https:",
  "media-src 'none'",
  "frame-src 'none'",
  "frame-ancestors 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  // upgrade-insecure-requests alleen in productie (HTTP→HTTPS)
  ...(!isDev ? ["upgrade-insecure-requests"] : []),
].join("; ");

const securityHeaders = [
  // HSTS — 1 jaar, inclusief subdomeinen, preload (nl.internet.nl vereiste)
  {
    key: "Strict-Transport-Security",
    value: "max-age=31536000; includeSubDomains; preload",
  },
  // CSP
  {
    key: "Content-Security-Policy",
    value: CSP,
  },
  // Klikjacking-bescherming
  {
    key: "X-Frame-Options",
    value: "DENY",
  },
  // MIME-sniffing voorkomen
  {
    key: "X-Content-Type-Options",
    value: "nosniff",
  },
  // Referrer beperken
  {
    key: "Referrer-Policy",
    value: "strict-origin-when-cross-origin",
  },
  // Gevoelige browser-API's uitschakelen
  {
    key: "Permissions-Policy",
    value: "camera=(), microphone=(), geolocation=(), interest-cohort=()",
  },
];

const nextConfig = {
  output: "standalone",

  // Maak de commit hash beschikbaar als omgevingsvariabele in de browser.
  env: {
    NEXT_PUBLIC_COMMIT_SHA: COMMIT_SHA,
    NEXT_PUBLIC_BUILD_TIMESTAMP: BUILD_TIMESTAMP,
  },

  async headers() {
    return [
      {
        // Beveiligingsheaders op alle routes
        source: "/(.*)",
        headers: securityHeaders,
      },
    ];
  },

  async rewrites() {
    return {
      beforeFiles: [
        {
          source: "/api/:path*",
          destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/:path*`,
        },
      ],
    };
  },
};

module.exports = nextConfig;
