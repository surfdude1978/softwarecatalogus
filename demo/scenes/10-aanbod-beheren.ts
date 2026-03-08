import { Page } from 'playwright';
import { BASE_URL } from '../helpers/config';
import { medium, long, waitForStable, scrollIntoView } from '../helpers/timing';
import { showStep, highlightElement } from '../helpers/overlay';
import { loginApi } from '../helpers/auth';

export const name = '10-aanbod-beheren';
export const title = 'Pakketaanbod beheren';

export async function run(page: Page): Promise<void> {
  // Verse context — stil inloggen als leverancier
  await loginApi(page, 'leverancier');
  await page.goto(`${BASE_URL}/aanbod`);
  await waitForStable(page);

  // Wacht extra op de tabel of lege staat — de AuthGuard doet een fetchProfile-ronde
  // waarna useEigenPakketten pas de pakketten-API aanroept (twee HTTP-rondes).
  await page
    .locator('table, text=U heeft nog geen pakketten, text=Eerste pakket aanmaken')
    .first()
    .waitFor({ state: 'visible', timeout: 12000 })
    .catch(() => {});

  // Guard: als we teruggestuurd zijn naar /login, is auth mislukt — toon foutmelding in video
  if (page.url().includes('/login')) {
    await showStep(
      page,
      21,
      '⚠ Leverancier-pagina niet bereikbaar',
      'Controleer of het /aanbod-dashboard actief is en het leverancier-account bestaat in de backend.'
    );
    await long(4000);
    return;
  }

  // ── Stap 21: Overzicht eigen pakketten ────────────────────────────────────────
  await showStep(
    page,
    21,
    'Pakketaanbod — Centric',
    'Overzicht van alle pakketten van Centric: naam, versie, licentievorm, status en het aantal gebruikende gemeenten.'
  );
  await long(2800);

  // Highlight de pakketlijst of de "Eerste pakket"-knop (lege state)
  const tabel = page.locator('table tbody tr').first();
  const legeState = page.locator('text=Eerste pakket aanmaken').first();

  if (await tabel.count()) {
    await highlightElement(page, 'table tbody tr:first-child', '#4A90D9', 1800);
    await medium(1600);

    // Highlight de status-badge in de eerste rij
    await highlightElement(page, 'table tbody tr:first-child td:nth-child(3)', '#F59E0B', 1500);
    await medium(1200);
  } else if (await legeState.count()) {
    await highlightElement(page, 'a:has-text("Eerste pakket aanmaken"), a:has-text("Nieuw pakket")', '#4A90D9', 1800);
    await medium(1400);
  }

  // ── Stap 22: Concept-status patroon ──────────────────────────────────────────
  await showStep(
    page,
    22,
    'Concept-status patroon',
    'Nieuwe pakketten krijgen automatisch "concept"-status en zijn pas zichtbaar na fiattering door VNG Realisatie.'
  );

  // Highlight het info-blok over concept-status
  await highlightElement(page, '[class*="amber"], [class*="bg-amber"]', '#F59E0B', 2000);
  await medium(1800);

  // Hover over de "Nieuw pakket" knop
  const nieuweBtn = page.locator('a:has-text("Nieuw pakket")').first();
  if (await nieuweBtn.count()) {
    await nieuweBtn.hover({ timeout: 3000 }).catch(() => {});
    await medium(1200);
  }

  // ── Stap 23: Formulier voor nieuw pakket ─────────────────────────────────────
  await showStep(
    page,
    23,
    'Nieuw pakket aanmaken',
    'Het formulier bevat: naam, versie, omschrijving, licentievorm en links naar website en documentatie.'
  );
  await page.goto(`${BASE_URL}/aanbod/nieuw`);
  await waitForStable(page);
  await medium(1200);

  // Highlight het naam-veld
  await highlightElement(page, '#naam', '#4A90D9', 1500);
  await medium(1800);

  // Highlight licentievorm-dropdown
  await highlightElement(page, '#licentievorm', '#4A90D9', 1500);
  await medium(1400);

  await scrollIntoView(page, 'body');
  await long(1500);
}
