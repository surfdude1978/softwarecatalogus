import { Page } from 'playwright';
import { BASE_URL, ACCOUNTS } from '../helpers/config';
import { short, medium, long, waitForStable } from '../helpers/timing';
import { showStep, showChapterTitle, hideChapterTitle } from '../helpers/overlay';
import { loginApi, logout } from '../helpers/auth';

export const name = '11-login-admin';
export const title = 'Login — Functioneel beheerder';

export async function run(page: Page): Promise<void> {
  // Uitloggen uit leverancier-sessie
  await logout(page);
  await waitForStable(page);

  await showChapterTitle(
    page,
    'Deel D — Functioneel beheerder',
    'Lisa de Vries · VNG Realisatie'
  );
  await long(2500);
  await hideChapterTitle(page);
  await short(500);

  await showStep(
    page,
    23,
    'Inloggen als Functioneel beheerder',
    `Email: ${ACCOUNTS.admin.email} — Volledige beheerstoegang`
  );
  await medium(1200);

  await loginApi(page, 'admin');
  await page.goto(`${BASE_URL}/beheer/organisaties`);
  await waitForStable(page);
}
