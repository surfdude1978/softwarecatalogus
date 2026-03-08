import { Page } from 'playwright';

// ─── Timing helpers ────────────────────────────────────────────────────────────
// Demo-tempo: ruim genoeg om te lezen, snel genoeg om te boeien.
// Pas SLOW_FACTOR aan op de commando-regel om alles te vertragen of versnellen.

const SLOW_FACTOR = parseFloat(process.env['DEMO_SLOW'] ?? '1.0');

const wait = (ms: number) =>
  new Promise<void>((r) => setTimeout(r, Math.round(ms * SLOW_FACTOR)));

/** Korte pauze — kijker "leest" de annotatie */
export const short  = (ms = 1200) => wait(ms);

/** Middellange pauze — scène-overgang of visuele verwerking */
export const medium = (ms = 2000) => wait(ms);

/** Lange pauze — hoofdstuktitel of eindshot */
export const long   = (ms = 3000) => wait(ms);

/** Wacht tot loading-spinners weg zijn én netwerk stil */
export async function waitForStable(page: Page, timeout = 10000): Promise<void> {
  await page.waitForLoadState('networkidle', { timeout }).catch(() => {});
  await page
    .locator('[data-loading="true"], .animate-pulse, [aria-busy="true"]')
    .waitFor({ state: 'detached', timeout: 4000 })
    .catch(() => {});
  await wait(600);
}

/** Wacht op een specifiek element zichtbaar */
export async function waitForVisible(
  page: Page,
  selector: string,
  timeout = 8000
): Promise<void> {
  await page.locator(selector).first().waitFor({ state: 'visible', timeout });
}

/** Typ met menselijk tempo (standaard ~80 ms per karakter) */
export async function humanType(
  page: Page,
  selector: string,
  text: string,
  delay = 80
): Promise<void> {
  await page.locator(selector).click();
  await page.locator(selector).clear();
  await wait(300);
  await page.keyboard.type(text, { delay });
}

/** Smooth-scroll tot een element in beeld is */
export async function scrollIntoView(page: Page, selector: string): Promise<void> {
  await page.locator(selector).scrollIntoViewIfNeeded().catch(() => {});
  await wait(700);
}
