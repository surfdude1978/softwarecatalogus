import { Page } from 'playwright';
import { BASE_URL } from '../helpers/config';
import { medium, long, waitForStable } from '../helpers/timing';
import { showStep, highlightElement } from '../helpers/overlay';
import { loginApi } from '../helpers/auth';

export const name = '12-organisatiebeheer';
export const title = 'Organisatiebeheer';

export async function run(page: Page): Promise<void> {
  // Verse context — stil inloggen als admin
  await loginApi(page, 'admin');
  await page.goto(`${BASE_URL}/beheer/organisaties`);
  await waitForStable(page);

  await showStep(
    page,
    24,
    'Organisatiebeheer',
    'Functioneel beheerder beheert alle organisaties en fiatterert nieuwe aanmeldingen van leveranciers en gemeenten.'
  );
  await long(2800);

  // Highlight de "wachtend op fiattering"-sectie
  const fiatteringTekst = page.locator('text=Wachtend op fiattering').first();
  if (await fiatteringTekst.count()) {
    await highlightElement(page, 'text=Wachtend op fiattering', '#F59E0B', 2000);
    await medium(1800);

    // Hover over de Fiatteren-knop
    const fiatterBtn = page.locator('button:has-text("Fiatteren")').first();
    if (await fiatterBtn.count()) {
      await showStep(
        page,
        25,
        'Fiattering — NieuweSoftware BV',
        'De beheerder keurt een nieuwe leverancier goed. Na fiattering wordt de organisatie "actief" en kunnen pakketten geregistreerd worden.'
      );
      await fiatterBtn.hover();
      await long(2500);
    }
  }
}
