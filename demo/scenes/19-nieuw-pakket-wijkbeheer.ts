import { Page } from 'playwright';
import { BASE_URL } from '../helpers/config';
import { short, medium, long, waitForStable, humanType, scrollIntoView } from '../helpers/timing';
import { showStep, highlightElement } from '../helpers/overlay';
import { loginApi, selectOption } from '../helpers/auth';

export const name = '19-nieuw-pakket-wijkbeheer';
export const title = 'Pakket aanmaken — WijkBeheer Pro';

export async function run(page: Page): Promise<void> {
  // Pieter logt in (account aangemaakt in scène 17, gefiatteerd in scène 18)
  await loginApi(page, 'pieter');
  await page.goto(`${BASE_URL}/aanbod`);
  await waitForStable(page);

  // Guard: niet ingelogd = fiattering nog niet gedaan
  if (page.url().includes('/login')) {
    await showStep(
      page,
      36,
      '⚠ Pieter kan niet inloggen',
      'Voer eerst scène 17 (registratie) en scène 18 (fiattering) uit voordat u deze scène opneemt.'
    );
    await long(4000);
    return;
  }

  // ── Stap 1: Aanbod-dashboard Pieter ──────────────────────────────────────────
  await showStep(
    page,
    36,
    'Dashboard TechSolutions BV',
    'Pieter van Dijk is ingelogd als aanbod-beheerder. Zijn dashboard toont het pakketaanbod van TechSolutions BV.'
  );
  await long(2800);

  // Highlight "Nieuw pakket" knop
  await highlightElement(
    page,
    'a:has-text("Nieuw pakket"), a:has-text("Eerste pakket aanmaken")',
    '#4A90D9',
    1800
  );
  await medium(1200);

  // ── Navigeer naar het aanmaakformulier ───────────────────────────────────────
  await showStep(
    page,
    37,
    'Nieuw pakket aanmaken',
    'Pieter registreert "WijkBeheer Pro" — software voor integraal beheer van de openbare ruimte.'
  );
  await page.goto(`${BASE_URL}/aanbod/nieuw`);
  await waitForStable(page);
  await medium(1200);

  // ── Stap 2: Basisgegevens invullen ───────────────────────────────────────────
  await highlightElement(page, '#naam', '#4A90D9', 1200);
  await humanType(page, '#naam', 'WijkBeheer Pro', 80);
  await short(600);

  await humanType(page, '#versie', '3.0', 80);
  await short(500);

  // Beschrijving
  const beschrijvingField = page.locator('#beschrijving, textarea').first();
  if (await beschrijvingField.count()) {
    await beschrijvingField.click();
    await page.keyboard.type(
      'Integraal beheer van de openbare ruimte voor gemeenten. Inclusief meldingenbeheer, inspectieronden en rapportages.',
      { delay: 30 }
    );
    await short(600);
  }

  await medium(1200);

  // ── Stap 3: GEMMA-component koppelen ─────────────────────────────────────────
  await showStep(
    page,
    38,
    'GEMMA-component koppelen',
    'WijkBeheer Pro wordt gekoppeld aan het GEMMA-referentiecomponent "Zaaksysteem". Dit bepaalt de positie op de architectuurkaart.'
  );
  await scrollIntoView(page, 'input[placeholder*="Zoek GEMMA"], input[placeholder*="GEMMA"]');
  await medium(1000);

  const gemmaSearch = page.locator('input[placeholder*="Zoek GEMMA"], input[placeholder*="GEMMA"]').first();
  if (await gemmaSearch.count()) {
    await highlightElement(page, 'input[placeholder*="Zoek GEMMA"], input[placeholder*="GEMMA"]', '#4A90D9', 1200);
    await gemmaSearch.click();
    await page.keyboard.type('Zaaksysteem', { delay: 80 });
    await waitForStable(page);
    await medium(1200);

    // Klik op het label of checkbox van Zaaksysteem
    const zaakLabel = page.locator('label').filter({ hasText: 'Zaaksysteem' }).first();
    const zaakCheckbox = page.locator('input[type="checkbox"]').filter({}).first();

    if (await zaakLabel.count()) {
      await highlightElement(page, 'label:has-text("Zaaksysteem")', '#10B981', 1200);
      await zaakLabel.click();
      await short(600);
    } else if (await zaakCheckbox.count()) {
      await zaakCheckbox.click();
      await short(600);
    }
    await medium(1000);
  }

  // ── Stap 4: Licentievorm en links ────────────────────────────────────────────
  await showStep(
    page,
    39,
    'Licentievorm en links',
    'Licentievorm: SaaS (cloud-hosted). Website: wijkbeheerpro.nl'
  );

  await selectOption(page, '#licentievorm', 'saas');
  await short(600);

  await scrollIntoView(page, '#website_url, input[name*="website"]');
  await humanType(page, '#website_url', 'https://wijkbeheerpro.nl', 60);
  await medium(1200);

  // ── Stap 5: Opslaan ──────────────────────────────────────────────────────────
  await showStep(
    page,
    40,
    'Pakket opslaan',
    'Na opslaan krijgt WijkBeheer Pro "concept"-status en is direct zichtbaar in de catalogus met concept-badge.'
  );
  await medium(800);

  const submitBtn = page.locator('button[type="submit"]:has-text("aanmaken"), button[type="submit"]').last();
  await scrollIntoView(page, 'button[type="submit"]');
  await highlightElement(page, 'button[type="submit"]', '#10B981', 1200);
  await medium(800);
  await submitBtn.click();
  await waitForStable(page);
  await long(2000);

  // ── Stap 6: Resultaat in /aanbod ─────────────────────────────────────────────
  // Na submit → redirect naar /aanbod
  if (!page.url().includes('/aanbod')) {
    await page.goto(`${BASE_URL}/aanbod`);
    await waitForStable(page);
  }

  await showStep(
    page,
    41,
    'WijkBeheer Pro aangemaakt ✓',
    'Het pakket staat in de lijst met "Concept"-badge. Het is nu ook zichtbaar in de publieke catalogus.'
  );

  // Highlight WijkBeheer Pro in de lijst
  const pakketRij = page.locator('tr, li, [class*="card"]').filter({ hasText: 'WijkBeheer Pro' }).first();
  if (await pakketRij.count()) {
    await pakketRij.scrollIntoViewIfNeeded().catch(() => {});
    await highlightElement(page, 'tr:has-text("WijkBeheer"), li:has-text("WijkBeheer"), [class*="card"]:has-text("WijkBeheer")', '#10B981', 2000);
  }
  await long(2800);

  // ── Stap 7: Detailpagina vanuit catalogus ────────────────────────────────────
  await showStep(
    page,
    42,
    'Pakketdetail in catalogus',
    'Gemeenten kunnen het pakket al vinden in de catalogus. GEMMA-component badge toont de koppeling met "Zaaksysteem".'
  );
  await page.goto(`${BASE_URL}/pakketten`);
  await waitForStable(page);

  // Zoek WijkBeheer Pro in de catalogus
  const zoekBalk = page.locator('input[placeholder*="Zoek"]').first();
  if (await zoekBalk.count()) {
    await zoekBalk.click();
    await page.keyboard.type('WijkBeheer', { delay: 80 });
    const zoekBtn = page.locator('button:has-text("Zoeken")').first();
    if (await zoekBtn.count()) await zoekBtn.click();
    await waitForStable(page);
    await medium(1200);
  }

  // Klik door naar detailpagina
  const pakketLink = page.locator('a').filter({ hasText: 'WijkBeheer Pro' }).first();
  if (await pakketLink.count()) {
    await pakketLink.click();
    await waitForStable(page);
    await medium(1200);

    await highlightElement(page, '[class*="badge"], .badge', '#10B981', 1800);
    await long(2500);
  } else {
    await long(2000);
  }
}
