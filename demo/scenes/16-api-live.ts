import { Page } from 'playwright';
import { BASE_URL } from '../helpers/config';
import { medium, long, waitForStable } from '../helpers/timing';
import { showStep, showChapterTitle, hideChapterTitle } from '../helpers/overlay';

export const name = '16-api-live';
export const title = 'Live API-call — JSON response';

export async function run(page: Page): Promise<void> {
  await showChapterTitle(page, 'Live API-demonstratie', 'Directe JSON-response in de browser');
  await long(2500);
  await hideChapterTitle(page);

  // Open API-response rechtstreeks in browser
  await page.goto(`${BASE_URL}/api/v1/pakketten/?format=json`);
  await waitForStable(page);

  await showStep(
    page,
    34,
    'GET /api/v1/pakketten/ — Live JSON',
    'Publieke API-response: paginated JSON met alle pakketten. Direkt bruikbaar voor integraties en dashboards.'
  );
  await long(3000);

  // Standaarden endpoint
  await page.goto(`${BASE_URL}/api/v1/standaarden/?format=json`);
  await waitForStable(page);

  await showStep(
    page,
    35,
    'GET /api/v1/standaarden/',
    'Alle standaarden als JSON: naam, type (verplicht/aanbevolen), versie en Forum Standaardisatie-URL.'
  );
  await long(2500);

  // GEMMA endpoint
  await page.goto(`${BASE_URL}/api/v1/gemma/componenten/?format=json`);
  await waitForStable(page);

  await showStep(
    page,
    36,
    'GET /api/v1/gemma/componenten/',
    '25 GEMMA-componenten als JSON. Inclusief ArchiMate-ID, type en hiërarchie. Importeerbaar in BI-tools.'
  );
  await long(2800);

  // Eindslide
  await showChapterTitle(
    page,
    'Demo voltooid ✓',
    'Softwarecatalogus — VNG Realisatie · EUPL-1.2 open source'
  );
  await long(3500);
  await hideChapterTitle(page);
  await medium();
}
