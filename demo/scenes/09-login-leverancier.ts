import { Page } from 'playwright';
import { BASE_URL, ACCOUNTS } from '../helpers/config';
import { short, medium, long, waitForStable } from '../helpers/timing';
import { showStep, showChapterTitle, hideChapterTitle } from '../helpers/overlay';
import { loginApi } from '../helpers/auth';

export const name = '09-login-leverancier';
export const title = 'Login — Leverancier Centric';

export async function run(page: Page): Promise<void> {
  await page.goto(`${BASE_URL}/login`);
  await waitForStable(page);

  await showChapterTitle(
    page,
    'Deel C — Leverancier aanbod-beheerder',
    `${ACCOUNTS.leverancier.naam} · ${ACCOUNTS.leverancier.org}`
  );
  await long(2500);
  await hideChapterTitle(page);
  await short(500);

  await showStep(
    page,
    20,
    'Inloggen als Aanbod-beheerder',
    `Email: ${ACCOUNTS.leverancier.email} — Rol: ${ACCOUNTS.leverancier.rol}`
  );
  await medium(1200);

  // Vul formulier in zichtbaar (langzaam typen voor de demo)
  await page.locator('input[type="email"]').click();
  await page.keyboard.type(ACCOUNTS.leverancier.email, { delay: 90 });
  await medium();
  await page.locator('input[type="password"]').click();
  await page.keyboard.type(ACCOUNTS.leverancier.password, { delay: 80 });
  await medium();

  // Inloggen via API voor gegarandeerd succes
  await showStep(page, 20, 'Inloggen…', 'Validatie en JWT-token ophalen via de beveiligde API.');
  await loginApi(page, 'leverancier');
  await page.goto(`${BASE_URL}/aanbod`);
  await waitForStable(page);

  // Guard: terugval naar /login = auth of routering mislukt
  if (page.url().includes('/login')) {
    await showStep(
      page,
      20,
      '⚠ /aanbod niet bereikbaar',
      'Controleer het leverancier-account en de /aanbod-route in de applicatie.'
    );
    await long(3500);
  }
}
