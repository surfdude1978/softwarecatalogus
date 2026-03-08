import { Page } from 'playwright';
import { BASE_URL } from '../helpers/config';
import { short, medium, long, waitForStable, scrollIntoView } from '../helpers/timing';
import { showStep, highlightElement } from '../helpers/overlay';
import { loginApi } from '../helpers/auth';

export const name = '07-mijn-landschap';
export const title = 'Mijn pakketlandschap';

export async function run(page: Page): Promise<void> {
  // Elke scène heeft een verse context — stil inloggen als gemeente
  await loginApi(page, 'gemeente');
  await page.goto(`${BASE_URL}/mijn-landschap`);
  await waitForStable(page);

  // Guard: terugval naar /login = auth of routering mislukt
  if (page.url().includes('/login')) {
    await showStep(
      page,
      16,
      '⚠ Mijn landschap niet bereikbaar',
      'Controleer het gemeente-account en de /mijn-landschap-route in de applicatie.'
    );
    await long(3500);
    return;
  }

  await showStep(
    page,
    16,
    'Mijn pakketlandschap — Gemeente Utrecht',
    'Overzicht van alle softwarepakketten in gebruik bij Gemeente Utrecht.'
  );
  await long(2800);

  // Scroll en highlight eerste pakket
  const eersteKaart = page.locator('main li, main [class*="card"], main [class*="item"]').first();
  if (await eersteKaart.count()) {
    await highlightElement(
      page,
      'main li:first-child, main [class*="card"]:first-child',
      '#10B981',
      1500
    );
  }
  await medium(1800);

  // Scroll naar beneden om meer pakketten te zien
  await showStep(
    page,
    17,
    'Pakket toevoegen',
    'Via "Pakket toevoegen" selecteert de beheerder een pakket uit de catalogus om toe te voegen aan het landschap.'
  );
  await page
    .locator('button:has-text("Pakket toevoegen"), a:has-text("Pakket toevoegen")')
    .first()
    .hover({ timeout: 3000 })
    .catch(() => {
      // Knop niet gevonden — stap overslaan
    });
  await medium(1600);

  // Profiel bekijken
  await showStep(page, 18, 'Mijn profiel', 'Naam, e-mail, rol en organisatie-instellingen.');
  await page
    .locator('text=Mijn profiel, a[href*="profiel"], nav >> text=Profiel')
    .first()
    .click({ timeout: 4000 })
    .catch(() => {
      // Profiellink niet gevonden — doorgaan
    });
  await waitForStable(page);
  await long(2000);
  await scrollIntoView(page, 'body');
}
