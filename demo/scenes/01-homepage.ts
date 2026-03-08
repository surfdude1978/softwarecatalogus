import { Page } from 'playwright';
import { BASE_URL } from '../helpers/config';
import { short, medium, long, waitForStable } from '../helpers/timing';
import { showStep, showChapterTitle, hideChapterTitle } from '../helpers/overlay';

export const name = '01-homepage';
export const title = 'Homepage';

export async function run(page: Page): Promise<void> {
  // Hoofdstuktitel
  await page.goto(`${BASE_URL}/`);
  await waitForStable(page);
  await showChapterTitle(page, 'Deel A — Publiek raadplegen', 'Geen inloggen vereist');
  await long(2500);
  await hideChapterTitle(page);
  await short(600);

  // Stap 1: Homepage
  await showStep(
    page,
    1,
    'Homepage — Softwarecatalogus',
    'Het centrale platform voor Nederlandse gemeenten om software te registreren, vergelijken en raadplegen.'
  );
  await long(2800);

  // Hover over de drie feature-blokken
  await page.locator('text=Catalogus doorzoeken').hover();
  await medium(1200);
  await page.locator('text=Gluren bij de buren').hover();
  await medium(1200);
  await page.locator('text=GEMMA architectuur').hover();
  await medium(1400);

  // Klik naar pakketten
  await page.locator('text=Bekijk de catalogus').click();
  await waitForStable(page);
}
