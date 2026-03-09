import { Page } from 'playwright';
import { BASE_URL } from '../helpers/config';
import { short, medium, long, waitForStable } from '../helpers/timing';
import { showStep, showChapterTitle, hideChapterTitle, highlightElement } from '../helpers/overlay';
import { selectOption } from '../helpers/auth';

export const name = '17-registreer-leverancier';
export const title = 'Leverancier registratie — TechSolutions BV';

export async function run(page: Page): Promise<void> {
  await page.goto(`${BASE_URL}/`);
  await page.waitForLoadState('domcontentloaded');

  // Hoofdstuktitel
  await showChapterTitle(
    page,
    'Demo — Volledige registratiestroom',
    'Leverancier → Fiattering → Pakket aanmaken → Gemeente koppelt → GEMMA-kaart'
  );
  await long(3000);
  await hideChapterTitle(page);
  await short(500);

  // Navigeer naar registratieformulier
  await page.goto(`${BASE_URL}/registreer/organisatie`);
  await waitForStable(page);

  // ── Stap 1: Registratieformulier uitleggen ──────────────────────────────────
  await showStep(
    page,
    27,
    'Nieuwe leverancier registreren',
    'Via het registratieformulier meldt TechSolutions BV zich aan. Organisatiegegevens en gebruikersaccount in één stroom.'
  );
  await long(2500);

  // Highlight organisatienaam-veld
  await highlightElement(page, '#org-naam', '#4A90D9', 1500);
  await medium(1200);

  // ── Stap 2: Stap 1 invullen (organisatie) ────────────────────────────────────
  await showStep(
    page,
    28,
    'Stap 1 — Organisatiegegevens',
    'Naam: TechSolutions BV · Type: Leverancier · Website: techsolutions.nl'
  );

  // Naam organisatie — gebruik fill() voor correcte React-events
  await page.locator('#org-naam').click();
  await page.locator('#org-naam').fill('TechSolutions BV');
  await short(700);

  // Type: Leverancier
  await highlightElement(page, '#org-type', '#F59E0B', 1000);
  await selectOption(page, '#org-type', 'leverancier');
  await short(600);

  // Website
  await page.locator('#org-website').click();
  await page.locator('#org-website').fill('https://techsolutions.nl');
  await medium(1200);

  // Volgende stap
  const volgendeBtn = page.locator('button:has-text("Volgende")').first();
  await volgendeBtn.scrollIntoViewIfNeeded().catch(() => {});
  await highlightElement(page, 'button:has-text("Volgende")', '#10B981', 1200);
  await volgendeBtn.click();
  await waitForStable(page);
  await short(800);

  // ── Stap 3: Stap 2 invullen (gebruiker) ──────────────────────────────────────
  await showStep(
    page,
    29,
    'Stap 2 — Gebruikersaccount',
    'Pieter van Dijk wordt de aanbod-beheerder van TechSolutions BV.'
  );
  await medium(1200);

  // Naam gebruiker — gebruik fill() voor correcte React-events
  await page.locator('#user-naam').fill('Pieter van Dijk');
  await short(600);

  // E-mail
  await page.locator('#user-email').fill('pieter@techsolutions.nl');
  await short(600);

  // Wachtwoord
  await page.locator('#user-password').fill('Welkom12345!');
  await short(500);

  // Wachtwoord bevestigen
  await page.locator('#user-password-confirm').fill('Welkom12345!');
  await short(500);

  await medium(1200);

  // ── Stap 4: Indienen ──────────────────────────────────────────────────────────
  await showStep(
    page,
    30,
    'Registratie indienen',
    'Na indiening krijgt de organisatie "concept"-status en wacht op fiattering door VNG Realisatie.'
  );
  await highlightElement(page, 'button:has-text("Registratie indienen")', '#10B981', 1500);
  await medium(800);

  const submitBtn = page.locator('button:has-text("Registratie indienen")').first();
  await submitBtn.click();
  await waitForStable(page);
  await long(2000);

  // ── Stap 5: Succespagina ──────────────────────────────────────────────────────
  await showStep(
    page,
    31,
    'Registratie ingediend ✓',
    'TechSolutions BV en Pieter van Dijk staan klaar voor fiattering. Pieter ontvangt een e-mail zodra zijn account actief is.'
  );
  await long(3500);
}
