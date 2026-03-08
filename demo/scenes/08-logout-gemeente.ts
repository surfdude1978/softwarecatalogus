import { Page } from 'playwright';
import { BASE_URL } from '../helpers/config';
import { short, medium, waitForStable } from '../helpers/timing';
import { showStep } from '../helpers/overlay';
import { loginApi, logout } from '../helpers/auth';

export const name = '08-logout-gemeente';
export const title = 'Uitloggen — Gemeente';

export async function run(page: Page): Promise<void> {
  // Stille login — zodat er een sessie is om te demonstreren hoe uitloggen werkt
  await loginApi(page, 'gemeente');
  await page.goto(`${BASE_URL}/mijn-landschap`);
  await waitForStable(page);

  await showStep(
    page,
    19,
    'Uitloggen',
    'Sessie afsluiten. JWT-tokens worden verwijderd, gebruiker wordt teruggeleid naar de inlogpagina.'
  );
  await medium();

  // Probeer de UI-uitlogknop; anders via logout-helper
  const uitlogBtn = page.locator('button:has-text("Uitloggen")').first();
  if (await uitlogBtn.count()) {
    await uitlogBtn.evaluate((el: HTMLElement) => el.click());
  } else {
    await logout(page);
  }

  await waitForStable(page);
  await page.goto(`${BASE_URL}/login`);
  await waitForStable(page);
  await short(800);
}
