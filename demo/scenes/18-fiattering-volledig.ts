import { Page } from 'playwright';
import { BASE_URL } from '../helpers/config';
import { medium, long, waitForStable } from '../helpers/timing';
import { showStep, highlightElement } from '../helpers/overlay';
import { loginApi } from '../helpers/auth';

export const name = '18-fiattering-volledig';
export const title = 'Fiattering — Organisatie en gebruiker';

export async function run(page: Page): Promise<void> {
  // Admin logt in (stil, via API)
  await loginApi(page, 'admin');
  await page.goto(`${BASE_URL}/beheer/organisaties`);
  await waitForStable(page);

  // ── Stap 1: Organisatiebeheer ─────────────────────────────────────────────────
  await showStep(
    page,
    32,
    'Organisatiebeheer — Fiattering TechSolutions BV',
    'De functioneel beheerder ziet de nieuw geregistreerde organisatie met "Concept"-status en keurt deze goed.'
  );
  await long(2500);

  // Highlight de organisatie in de lijst
  const techOrgRow = page.locator('li, tr').filter({ hasText: 'TechSolutions' }).first();
  if (await techOrgRow.count()) {
    await techOrgRow.scrollIntoViewIfNeeded().catch(() => {});
    await highlightElement(page, 'li:has-text("TechSolutions"), tr:has-text("TechSolutions")', '#F59E0B', 2000);
    await medium(1500);
  } else {
    // Fallback: highlight de sectie "Wachtend op fiattering"
    await highlightElement(page, 'text=Wachtend op fiattering', '#F59E0B', 1800);
    await medium(1500);
  }

  // ── Stap 2: Klik Fiatteren voor de organisatie ───────────────────────────────
  await showStep(
    page,
    33,
    'Organisatie fiatteren',
    'Na fiattering wordt TechSolutions BV "actief" — Pieter kan nu zijn account activeren.'
  );
  await medium(1200);

  // Zoek de Fiatteren-knop naast TechSolutions
  const fiatOrg = page
    .locator('li, tr')
    .filter({ hasText: 'TechSolutions' })
    .locator('button:has-text("Fiatteren")')
    .first();

  const fiatOrgFallback = page.locator('button:has-text("Fiatteren")').first();
  const orgBtn = (await fiatOrg.count()) ? fiatOrg : fiatOrgFallback;

  if (await orgBtn.count()) {
    // Scroll element naar midden van viewport via JS
    await orgBtn.evaluate((el) => el.scrollIntoView({ block: 'center', behavior: 'instant' }));
    await page.waitForTimeout(400);
    await orgBtn.hover({ timeout: 5000, force: true }).catch(() => {});
    await medium(1000);
    // Klik via DOM (omzeilt Playwright viewport-checks die false-positives geven in Xvfb)
    await orgBtn.evaluate((el) => (el as HTMLElement).click());
    await waitForStable(page);
    await long(2000);

    await showStep(
      page,
      33,
      'Organisatie gefiatteerd ✓',
      'TechSolutions BV is nu "actief" en verdwenen uit de wachtrij.'
    );
    await long(2000);
  } else {
    await showStep(
      page,
      33,
      'Geen organisaties in wachtrij',
      'TechSolutions BV is al gefiatteerd of de seed-data is nog niet geladen.'
    );
    await long(2500);
  }

  // ── Stap 3: Naar gebruikersbeheer ────────────────────────────────────────────
  await page.goto(`${BASE_URL}/beheer/gebruikers`);
  await waitForStable(page);

  await showStep(
    page,
    34,
    'Gebruikersbeheer — Fiattering Pieter van Dijk',
    'Pieter van Dijk wacht op fiattering. Na goedkeuring kan hij inloggen en pakketten registreren.'
  );
  await long(2500);

  // Highlight Pieter in de lijst
  const pieterRow = page.locator('li, tr').filter({ hasText: 'Pieter' }).first();
  if (await pieterRow.count()) {
    await pieterRow.scrollIntoViewIfNeeded().catch(() => {});
    await highlightElement(page, 'li:has-text("Pieter"), tr:has-text("Pieter")', '#4A90D9', 2000);
    await medium(1500);
  }

  // ── Stap 4: Klik Fiatteren voor de gebruiker ─────────────────────────────────
  await showStep(
    page,
    35,
    'Gebruiker fiatteren',
    'Met één klik wordt het account van Pieter geactiveerd.'
  );
  await medium(1000);

  const fiatUser = page
    .locator('li, tr')
    .filter({ hasText: 'Pieter' })
    .locator('button:has-text("Fiatteren")')
    .first();

  const fiatUserFallback = page.locator('button:has-text("Fiatteren")').first();
  const userBtn = (await fiatUser.count()) ? fiatUser : fiatUserFallback;

  if (await userBtn.count()) {
    await userBtn.evaluate((el) => el.scrollIntoView({ block: 'center', behavior: 'instant' }));
    await page.waitForTimeout(400);
    await userBtn.hover({ timeout: 5000, force: true }).catch(() => {});
    await medium(1000);
    // Klik via DOM (omzeilt Playwright viewport-checks)
    await userBtn.evaluate((el) => (el as HTMLElement).click());
    await waitForStable(page);
    await long(2000);

    await showStep(
      page,
      35,
      'Gebruiker gefiatteerd ✓',
      'Pieter van Dijk kan nu inloggen bij TechSolutions BV en pakketten registreren.'
    );
    await long(2500);
  } else {
    await showStep(
      page,
      35,
      'Geen gebruikers in wachtrij',
      'Pieter van Dijk is al gefiatteerd of de registratie uit scène 17 is nog niet voltooid.'
    );
    await long(2500);
  }
}
