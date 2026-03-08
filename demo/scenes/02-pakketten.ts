import { Page } from 'playwright';
import { BASE_URL } from '../helpers/config';
import { short, medium, long, waitForStable, humanType } from '../helpers/timing';
import { showStep, highlightElement } from '../helpers/overlay';
import { selectOption } from '../helpers/auth';

export const name = '02-pakketten';
export const title = 'Pakketcatalogus';

export async function run(page: Page): Promise<void> {
  await page.goto(`${BASE_URL}/pakketten`);
  await waitForStable(page);

  // Stap 2: Overzicht
  await showStep(
    page,
    2,
    'Pakketcatalogus',
    'Overzicht van alle 29 geregistreerde softwarepakketten. Zoek, filter en sorteer direct.'
  );
  await long(2500);

  // Highlight zoekbalk
  await highlightElement(page, 'input[placeholder*="Zoek"]', '#4A90D9', 1800);
  await medium();

  // Stap 3: Zoeken
  await showStep(page, 3, 'Zoeken op naam', 'Type "zaak" om zaakgerelateerde pakketten te vinden.');
  await humanType(page, 'input[placeholder*="Zoek"]', 'zaak', 100);
  await page.locator('button:has-text("Zoeken")').click();
  await waitForStable(page);
  await medium(1600);

  // Reset
  await page.locator('input[placeholder*="Zoek"]').clear();
  await page.locator('button:has-text("Zoeken")').click();
  await waitForStable(page);
  await short();

  // Stap 4: Filter SaaS
  await showStep(
    page,
    4,
    'Filter op licentievorm — SaaS',
    'Selecteer "SaaS" om alleen cloudgebaseerde pakketten te tonen. Van 29 naar 16 resultaten.'
  );
  await highlightElement(page, 'select', '#F59E0B', 1200);
  await short(700);
  await selectOption(page, 'select', 'saas');
  await waitForStable(page);
  await long(2200);

  // Stap 5: Sorteren
  await showStep(
    page,
    5,
    'Sorteren op populariteit',
    'Sorteer op "Meeste gemeenten" om de meest gebruikte SaaS-pakketten bovenaan te zien.'
  );
  const selects = page.locator('select');
  const count = await selects.count();
  if (count >= 3) {
    await page.evaluate(() => {
      const sels = document.querySelectorAll('select');
      const sortSel = sels[2] as HTMLSelectElement;
      const nativeSetter = Object.getOwnPropertyDescriptor(
        window.HTMLSelectElement.prototype, 'value'
      )!.set!;
      nativeSetter.call(sortSel, 'gemeenten');
      sortSel.dispatchEvent(new Event('change', { bubbles: true }));
    });
    await waitForStable(page);
    await long(2000);
  }

  // Reset filters
  await showStep(page, 5, 'Filters resetten', 'Terug naar alle 29 pakketten.');
  await selectOption(page, 'select', '');
  await waitForStable(page);
  await medium();
}
