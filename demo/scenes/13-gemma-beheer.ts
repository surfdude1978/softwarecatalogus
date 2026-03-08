import { Page } from 'playwright';
import { BASE_URL } from '../helpers/config';
import { medium, long, waitForStable, scrollIntoView } from '../helpers/timing';
import { showStep, highlightElement } from '../helpers/overlay';
import { loginApi } from '../helpers/auth';

export const name = '13-gemma-beheer';
export const title = 'GEMMA ArchiMate-beheer';

export async function run(page: Page): Promise<void> {
  // Verse context — stil inloggen als admin
  await loginApi(page, 'admin');
  await page.goto(`${BASE_URL}/beheer/gemma`);
  await waitForStable(page);

  await showStep(
    page,
    26,
    'GEMMA Beheer',
    'Beheer van GEMMA ArchiMate-referentiecomponenten. 25 componenten geladen uit de GEMMA-referentiearchitectuur.'
  );
  await long(2800);

  // Highlight de AMEFF-importsectie
  await showStep(
    page,
    27,
    'AMEFF-import',
    'Upload een ArchiMate Exchange Model File (XML) om de GEMMA-componentenbibliotheek bij te werken.'
  );
  await highlightElement(page, 'text=AMEFF importeren', '#4A90D9', 2000);
  const uploadBtn = page.locator('input[type="file"]').first();
  if (await uploadBtn.count()) {
    await highlightElement(page, 'input[type="file"]', '#4A90D9', 1500);
  }
  await medium(2000);

  // Scroll naar de componentenlijst
  await showStep(
    page,
    28,
    'GEMMA-componenten',
    '25 geregistreerde componenten: applicatiecomponenten en applicatieservices met ArchiMate-ID\'s.'
  );
  await scrollIntoView(page, 'text=GEMMA componenten');
  await highlightElement(page, 'text=GEMMA componenten', '#10B981', 1500);
  await long(2500);

  // Scroll om tabel te zien
  await page.mouse.wheel(0, 300);
  await medium(1800);
}
