import { Page } from 'playwright';
import { BASE_URL } from '../helpers/config';
import { medium, long, waitForStable, scrollIntoView } from '../helpers/timing';
import { showStep, showChapterTitle, hideChapterTitle, highlightElement } from '../helpers/overlay';

export const name = '15-api-swagger';
export const title = 'Publieke API — Swagger UI';

export async function run(page: Page): Promise<void> {
  // Swagger UI wordt door Django geserveerd op /api/v1/docs/ (drf-spectacular)
  await page.goto(`${BASE_URL}/api/v1/docs/`);
  // Swagger is JavaScript-zwaar — wacht tot de UI volledig is gerenderd
  await page.waitForLoadState('networkidle', { timeout: 20000 }).catch(() => {});
  await waitForStable(page);

  await showChapterTitle(
    page,
    'Deel E — Publieke REST API',
    'OpenAPI 3.x · NL API Strategie · Versie /api/v1/'
  );
  await long(2800);
  await hideChapterTitle(page);

  await showStep(
    page,
    31,
    'OpenAPI / Swagger UI',
    'Alle endpoints gedocumenteerd en interactief testbaar. Conform NL API Strategie en OAS 3.x.'
  );
  await long(2500);

  // Highlight de info-sectie bovenaan (titel + versie)
  await highlightElement(page, '.information-container, .info', '#4A90D9', 1500);
  await medium(1200);

  // Scroll naar pakketten-endpoint — Swagger gebruikt .opblock-summary-path voor paden
  await showStep(
    page,
    32,
    'GET /api/v1/pakketten/',
    'Publiek endpoint: geen authenticatie vereist. Ondersteunt zoek- en filterparameters.'
  );
  const pakkettenLocator = page
    .locator('.opblock-summary-path, span.url')
    .filter({ hasText: '/pakketten/' })
    .first();
  if (await pakkettenLocator.count()) {
    await pakkettenLocator.scrollIntoViewIfNeeded();
    await highlightElement(page, '.opblock-get:has(.opblock-summary-path:has-text("/pakketten/"))', '#22C55E', 1800);
    await long(2000);
  } else {
    // Fallback: scroll naar onderaan de pagina om endpoints te tonen
    await page.evaluate(() => window.scrollTo(0, 400));
    await long(2000);
  }

  // Scroll naar auth-endpoint
  await showStep(
    page,
    33,
    'POST /api/v1/auth/login/',
    'Authenticatie-endpoint: geeft JWT access- en refresh-token terug bij geldige credentials.'
  );
  const authLocator = page
    .locator('.opblock-summary-path, span.url')
    .filter({ hasText: '/auth/login/' })
    .first();
  if (await authLocator.count()) {
    await authLocator.scrollIntoViewIfNeeded();
    await highlightElement(page, '.opblock-post:has(.opblock-summary-path:has-text("/auth/login/"))', '#F59E0B', 1800);
    await medium(2000);
  } else {
    await page.evaluate(() => window.scrollTo(0, 800));
    await medium(2000);
  }

  // Toon schema-link
  await showStep(
    page,
    34,
    'OpenAPI schema — /api/v1/schema/',
    'Machineleesbare OAS 3.x spec: importeerbaar in Postman, Insomnia of eigen clients.'
  );
  await medium(2500);

  await scrollIntoView(page, 'body');
}
