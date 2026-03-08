import { Page } from 'playwright';
import { BASE_URL } from '../helpers/config';
import { medium, long, waitForStable, scrollIntoView } from '../helpers/timing';
import { showStep, highlightElement } from '../helpers/overlay';

export const name = '05-standaarden';
export const title = 'Standaarden';

export async function run(page: Page): Promise<void> {
  await page.goto(`${BASE_URL}/standaarden`);
  await waitForStable(page);

  await showStep(
    page,
    13,
    'Standaarden — Forum Standaardisatie',
    'Overzicht van verplichte en aanbevolen open standaarden voor gemeenten.'
  );
  await long(2500);

  // Highlight een "Verplicht"-badge
  await highlightElement(page, 'text=Verplicht', '#EF4444', 1800);
  await medium(1600);

  // Highlight een "Aanbevolen"-badge
  await highlightElement(page, 'text=Aanbevolen', '#F59E0B', 1800);
  await medium(1600);

  // Scroll om meer standaarden te tonen
  await showStep(
    page,
    14,
    'Forum Standaardisatie-links',
    'Elke standaard heeft een directe link naar het Forum Standaardisatie voor de volledige documentatie.'
  );
  await scrollIntoView(page, 'text=DigiD');
  await medium();
  await highlightElement(page, 'text=Forum Standaardisatie', '#4A90D9', 1500);
  await long(2000);
}
