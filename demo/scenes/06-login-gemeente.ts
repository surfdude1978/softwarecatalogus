import { Page } from 'playwright';
import { BASE_URL, ACCOUNTS } from '../helpers/config';
import { short, medium, long, waitForStable } from '../helpers/timing';
import { showStep, showChapterTitle, hideChapterTitle } from '../helpers/overlay';
import { loginApi } from '../helpers/auth';

export const name = '06-login-gemeente';
export const title = 'Login — Gemeente Utrecht';

export async function run(page: Page): Promise<void> {
  // Hoofdstuktitel
  await page.goto(`${BASE_URL}/login`);
  await waitForStable(page);
  await showChapterTitle(
    page,
    'Deel B — Gemeente gebruik-beheerder',
    'Jan Jansen · Gemeente Utrecht'
  );
  await long(2500);
  await hideChapterTitle(page);
  await short(500);

  // Toon het inlogscherm
  await showStep(
    page,
    15,
    'Inloggen als Gebruik-beheerder',
    `Email: ${ACCOUNTS.gemeente.email} — Rol: ${ACCOUNTS.gemeente.rol}`
  );
  await medium(1500);

  // Vul formulier in zichtbaar (langzaam typen voor de demo)
  await page.locator('input[type="email"]').click();
  await page.keyboard.type(ACCOUNTS.gemeente.email, { delay: 90 });
  await medium();
  await page.locator('input[type="password"]').click();
  await page.keyboard.type(ACCOUNTS.gemeente.password, { delay: 80 });
  await medium();

  // Klik inloggen — via API zodat we zeker zijn van succes
  await showStep(page, 15, 'Inloggen…', 'Validatie en JWT-token ophalen via de beveiligde API.');
  await loginApi(page, 'gemeente');
  await page.goto(`${BASE_URL}/mijn-landschap`);
  await waitForStable(page);
}
