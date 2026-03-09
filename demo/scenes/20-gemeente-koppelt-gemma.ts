import { Page } from 'playwright';
import { BASE_URL } from '../helpers/config';
import { short, medium, long, waitForStable, humanType, scrollIntoView } from '../helpers/timing';
import { showStep, highlightElement } from '../helpers/overlay';
import { loginApi } from '../helpers/auth';

export const name = '20-gemeente-koppelt-gemma';
export const title = 'Gemeente koppelt pakket + GEMMA architectuurkaart';

export async function run(page: Page): Promise<void> {
  // Utrecht gemeente logt in
  await loginApi(page, 'gemeente');
  await page.goto(`${BASE_URL}/mijn-landschap`);
  await waitForStable(page);

  // Guard
  if (page.url().includes('/login')) {
    await showStep(
      page,
      43,
      '⚠ Gemeente-account niet bereikbaar',
      'Controleer of het gemeente-account j.jansen@utrecht.nl bestaat in de backend.'
    );
    await long(3500);
    return;
  }

  // ── Stap 1: Huidig landschap van Utrecht ─────────────────────────────────────
  await showStep(
    page,
    43,
    'Mijn pakketlandschap — Gemeente Utrecht',
    'Jan Jansen (gebruik-beheerder Utrecht) wil WijkBeheer Pro toevoegen aan het software-landschap van de gemeente.'
  );
  await long(2500);

  // Highlight "Pakket toevoegen" knop
  const toevoegenBtn = page.locator('a:has-text("Pakket toevoegen"), button:has-text("Pakket toevoegen")').first();
  if (await toevoegenBtn.count()) {
    await highlightElement(page, 'a:has-text("Pakket toevoegen"), button:has-text("Pakket toevoegen")', '#4A90D9', 1800);
    await medium(1000);
    await toevoegenBtn.click();
  } else {
    await page.goto(`${BASE_URL}/pakketten`);
  }
  await waitForStable(page);

  // ── Stap 2: Zoeken in de catalogus ───────────────────────────────────────────
  await showStep(
    page,
    44,
    'Pakket zoeken — WijkBeheer Pro',
    'Jan zoekt in de catalogus naar "WijkBeheer" om het pakket van TechSolutions BV te vinden.'
  );
  await medium(1200);

  const zoekBalk = page.locator('input[placeholder*="Zoek"]').first();
  if (await zoekBalk.count()) {
    await highlightElement(page, 'input[placeholder*="Zoek"]', '#4A90D9', 1200);
    await humanType(page, 'input[placeholder*="Zoek"]', 'WijkBeheer', 90);
    const zoekBtn = page.locator('button:has-text("Zoeken")').first();
    if (await zoekBtn.count()) await zoekBtn.click();
    await waitForStable(page);
    await medium(1500);
  }

  // Klik op WijkBeheer Pro in de resultaten
  const pakketLink = page.locator('a').filter({ hasText: 'WijkBeheer Pro' }).first();
  if (await pakketLink.count()) {
    await highlightElement(page, 'a:has-text("WijkBeheer Pro"), h3:has-text("WijkBeheer")', '#10B981', 1500);
    await medium(800);
    await pakketLink.click();
    await waitForStable(page);
  } else {
    // Navigeer direct naar /pakketten en zoek de eerste pakket-link
    await page.goto(`${BASE_URL}/pakketten`);
    await waitForStable(page);
  }

  // ── Stap 3: Detailpagina — toevoegen ─────────────────────────────────────────
  await showStep(
    page,
    45,
    'WijkBeheer Pro detailpagina',
    'Op de detailpagina vindt Jan alle informatie: beschrijving, GEMMA-component "Zaaksysteem", licentievorm SaaS en de knop om het toe te voegen.'
  );
  await long(2500);

  // Highlight GEMMA-component badge
  const gemmaBadge = page.locator('[class*="badge"], .badge').filter({ hasText: 'Zaaksysteem' }).first();
  if (await gemmaBadge.count()) {
    await gemmaBadge.scrollIntoViewIfNeeded().catch(() => {});
    await highlightElement(page, '[class*="badge"]:has-text("Zaaksysteem"), .badge:has-text("Zaaksysteem")', '#6366F1', 2000);
    await medium(1500);
  }

  // ── Stap 4: "+ Aan mijn landschap" knop ──────────────────────────────────────
  await showStep(
    page,
    46,
    '+ Aan mijn landschap toevoegen',
    'Jan klikt op de knop om WijkBeheer Pro direct toe te voegen aan het pakketlandschap van Gemeente Utrecht.'
  );

  const toevoegenKnop = page.locator('button:has-text("Aan mijn landschap"), button:has-text("mijn landschap")').first();
  if (await toevoegenKnop.count()) {
    await scrollIntoView(page, 'button:has-text("Aan mijn landschap"), button:has-text("mijn landschap")');
    await highlightElement(page, 'button:has-text("Aan mijn landschap"), button:has-text("mijn landschap")', '#10B981', 2000);
    await medium(800);
    await toevoegenKnop.click();
    await waitForStable(page);
    await medium(1000);

    // Toon succesmelding
    await showStep(
      page,
      46,
      'Toegevoegd aan uw landschap ✓',
      'WijkBeheer Pro is opgeslagen als "In gebruik" in het pakketlandschap van Gemeente Utrecht.'
    );
    await highlightElement(page, 'text=Toegevoegd, span:has-text("Toegevoegd")', '#10B981', 2000);
    await long(2500);
  } else {
    await showStep(
      page,
      46,
      '⚠ Knop niet gevonden',
      'De "+ Aan mijn landschap"-knop is alleen zichtbaar voor ingelogde gebruik-beheerders.'
    );
    await long(3000);
  }

  // ── Stap 5: Terug naar mijn-landschap ────────────────────────────────────────
  await showStep(
    page,
    47,
    'Pakketlandschap — bijgewerkt',
    'In het overzicht ziet Jan WijkBeheer Pro met status "In gebruik". Het pakket is gekoppeld aan GEMMA-component Zaaksysteem.'
  );
  await page.goto(`${BASE_URL}/mijn-landschap`);
  await waitForStable(page);
  await medium(1500);

  // Highlight WijkBeheer Pro in het landschap
  const pakketInLandschap = page
    .locator('[class*="card"], li')
    .filter({ hasText: 'WijkBeheer Pro' })
    .first();

  if (await pakketInLandschap.count()) {
    await pakketInLandschap.scrollIntoViewIfNeeded().catch(() => {});
    await highlightElement(
      page,
      '[class*="card"]:has-text("WijkBeheer"), li:has-text("WijkBeheer")',
      '#10B981',
      2000
    );
    await long(2500);
  } else {
    await long(2000);
  }

  // ── Stap 6: GEMMA architectuurkaart ──────────────────────────────────────────
  await showStep(
    page,
    48,
    'GEMMA Architectuurkaart',
    'De architectuurkaart toont het volledige softwarelandschap van Gemeente Utrecht geprojecteerd op de GEMMA-referentiearchitectuur.'
  );

  const kaartBtn = page.locator('a:has-text("Architectuurkaart"), button:has-text("Architectuurkaart")').first();
  if (await kaartBtn.count()) {
    await kaartBtn.evaluate((el) => el.scrollIntoView({ block: 'center', behavior: 'instant' }));
    await page.waitForTimeout(400);
    await highlightElement(page, 'a:has-text("Architectuurkaart"), button:has-text("Architectuurkaart")', '#6366F1', 1800);
    await medium(800);
    try {
      await kaartBtn.click({ timeout: 5000, force: true });
    } catch {
      // Fallback: navigeer direct als klik mislukt
      await page.goto(`${BASE_URL}/mijn-landschap/architectuurkaart`);
    }
  } else {
    await page.goto(`${BASE_URL}/mijn-landschap/architectuurkaart`);
  }
  await waitForStable(page);
  await long(3000);

  // ── Stap 7: WijkBeheer Pro op de kaart ───────────────────────────────────────
  await showStep(
    page,
    49,
    'WijkBeheer Pro op de GEMMA-kaart',
    'WijkBeheer Pro verschijnt als groene badge bij het GEMMA-component "Zaaksysteem". Groen = in gebruik, geel = gepland.'
  );

  // Scroll naar Zaaksysteem sectie
  const zaaksysteemSectie = page.locator('text=Zaaksysteem').first();
  if (await zaaksysteemSectie.count()) {
    await zaaksysteemSectie.scrollIntoViewIfNeeded().catch(() => {});
    await medium(800);
    await highlightElement(page, 'text=Zaaksysteem', '#6366F1', 2500);
    await medium(1500);
  }

  // Highlight WijkBeheer Pro badge op de kaart
  const wijkBadge = page.locator('[class*="badge"], button, span').filter({ hasText: 'WijkBeheer Pro' }).first();
  if (await wijkBadge.count()) {
    await wijkBadge.scrollIntoViewIfNeeded().catch(() => {});
    await highlightElement(
      page,
      '[class*="badge"]:has-text("WijkBeheer"), button:has-text("WijkBeheer"), span:has-text("WijkBeheer")',
      '#10B981',
      2500
    );
    await long(2000);

    // Hover voor tooltip
    await wijkBadge.hover({ timeout: 3000 }).catch(() => {});
    await medium(1800);
  }

  // ── Stap 8: Legenda tonen ─────────────────────────────────────────────────────
  await showStep(
    page,
    50,
    'Legenda — kleurcodering',
    'Groen = in gebruik · Geel = gepland · Grijs = gestopt. De kaart is direct exporteerbaar als AMEFF voor ArchiMate-tools.'
  );

  const legenda = page.locator('text=In gebruik, text=legenda, [class*="legend"]').first();
  if (await legenda.count()) {
    await legenda.scrollIntoViewIfNeeded().catch(() => {});
    await highlightElement(page, 'text=In gebruik, [class*="legend"]', '#10B981', 2000);
  }
  await long(3500);

  await scrollIntoView(page, 'body');
}
