/** @type {import('next').NextConfig} */

// Content Security Policy voor productie (nl.internet.nl vereiste)
const CSP = [
  "default-src 'self'",
  // Next.js vereist unsafe-inline voor inline scripts (nonce-gebaseerde aanpak vereist extra middleware)
  "script-src 'self' 'unsafe-inline'",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob: https:",
  "font-src 'self' data:",
  "connect-src 'self' wss: https:",
  "media-src 'none'",
  "frame-src 'none'",
  "frame-ancestors 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "upgrade-insecure-requests",
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
