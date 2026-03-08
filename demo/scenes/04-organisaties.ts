import { Page } from 'playwright';
import { BASE_URL } from '../helpers/config';
import { medium, long, waitForStable, scrollIntoView } from '../helpers/timing';
import { showStep } from '../helpers/overlay';

export const name = '04-organisaties';
export const title = 'Organisaties';

export async function run(page: Page): Promise<void> {
  await page.goto(`${BASE_URL}/organisaties`);
  await waitForStable(page);

  await showStep(
    page,
    11,
    'Organisatiesoverzicht',
    'Alle geregistreerde organisaties: gemeenten, leveranciers en samenwerkingsverbanden.'
  );
  await long(2500);

  // Klik op eerste leverancier in de lijst
  const link = page.locator('a[href*="/organisaties/"]').first();
  if (await link.count()) {
    const naam = await link.textContent();
    await showStep(
      page,
      12,
      `Organisatiedetail — ${naam?.trim()}`,
      'Contactinformatie, type organisatie en alle geregistreerde pakketten.'
    );
    await link.hover();
    await medium();
    await link.click();
    await waitForStable(page);
    await long(2200);
    await scrollIntoView(page, 'body');
  }
}
