// ─── Centrale demo-configuratie ───────────────────────────────────────────────

// Lokaal (Node.js op Windows):  http://localhost
// Docker op Windows:            http://host.docker.internal
export const BASE_URL = process.env['DEMO_BASE_URL'] ?? 'http://localhost';

/** Viewport: 1600×900 = nette 16:9 voor rendering naar 1080p */
export const VIEWPORT = { width: 1600, height: 900 };

/** Opnameframerate voor video */
export const FPS = 30;

/** Demo-accounts (wachtwoord overal gelijk) */
export const ACCOUNTS = {
  gemeente: {
    email: 'j.jansen@utrecht.nl',
    password: 'Welkom01!',
    naam: 'Jan Jansen',
    rol: 'Gebruik-beheerder',
    org: 'Gemeente Utrecht',
  },
  leverancier: {
    email: 'verkoop@centric.eu',
    password: 'Welkom01!',
    naam: 'Hans Centric',
    rol: 'Aanbod-beheerder',
    org: 'Centric',
  },
  admin: {
    email: 'admin@vngrealisatie.nl',
    password: 'Welkom01!',
    naam: 'Lisa de Vries',
    rol: 'Functioneel beheerder',
    org: 'VNG Realisatie',
  },
  /** Nieuw account aangemaakt tijdens demo-registratiestroom (scène 17–19) */
  pieter: {
    email: 'pieter@techsolutions.nl',
    password: 'Welkom12345!',
    naam: 'Pieter van Dijk',
    rol: 'Aanbod-beheerder',
    org: 'TechSolutions BV',
  },
} as const;

/** Pad naar auth-storage-states */
export const AUTH_STATES = {
  gemeente: './auth/gemeente-utrecht.json',
  leverancier: './auth/leverancier-centric.json',
  admin: './auth/admin-vng.json',
} as const;

/** Output-directory voor clips */
export const OUTPUT_DIR = './output/clips';
