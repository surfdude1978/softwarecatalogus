/**
 * setup-auth.ts — Maak auth-storage-states aan voor alle demo-rollen
 *
 * Gebruik: npx ts-node setup-auth.ts
 *
 * Genereert:
 *   auth/gemeente-utrecht.json
 *   auth/leverancier-centric.json
 *   auth/admin-vng.json
 */

import * as path from 'path';
import * as fs from 'fs';
import { chromium } from 'playwright';
import { BASE_URL, ACCOUNTS, AUTH_STATES } from './helpers/config';

const AUTH_DIR = path.resolve(__dirname, 'auth');

async function setupRole(
  rolNaam: keyof typeof ACCOUNTS,
  statePath: string
): Promise<void> {
  const account = ACCOUNTS[rolNaam];
  console.log(`\n🔑 Auth aanmaken voor: ${account.naam} (${account.rol})`);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1600, height: 900 } });
  const page = await context.newPage();

  await page.goto(`${BASE_URL}/login`);
  await page.waitForLoadState('networkidle');

  // Login via API
  const result = await page.evaluate(
    async ({ email, password }) => {
      const csrf =
        document.cookie
          .split(';')
          .find((c) => c.trim().startsWith('csrftoken='))
          ?.split('=')[1] ?? '';

      const res = await fetch('/api/v1/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrf,
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json() as Record<string, unknown>;
      const access = (data['access_token'] ?? data['access']) as string | undefined;
      const refresh = (data['refresh_token'] ?? data['refresh']) as string | undefined;

      if (access) {
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh ?? '');
        return { ok: true, status: res.status };
      }
      return { ok: false, status: res.status, data };
    },
    { email: account.email, password: account.password }
  );

  if (!result.ok) {
    console.error(`  ✗ Login mislukt (status ${result.status})`);
    await browser.close();
    return;
  }

  // Sla storage-state op (localStorage + cookies)
  await context.storageState({ path: statePath });
  console.log(`  ✓ Opgeslagen: ${path.relative(process.cwd(), statePath)}`);

  await browser.close();
}

async function main() {
  if (!fs.existsSync(AUTH_DIR)) fs.mkdirSync(AUTH_DIR, { recursive: true });

  console.log('🔐 Auth-states aanmaken voor alle demo-rollen…');
  console.log(`   App URL: ${BASE_URL}`);

  await setupRole('gemeente', path.resolve(AUTH_DIR, 'gemeente-utrecht.json'));
  await setupRole('leverancier', path.resolve(AUTH_DIR, 'leverancier-centric.json'));
  await setupRole('admin', path.resolve(AUTH_DIR, 'admin-vng.json'));

  console.log('\n✅ Klaar! Auth-states staan in ./auth/');
}

main().catch((err) => {
  console.error('Fout:', err);
  process.exit(1);
});
