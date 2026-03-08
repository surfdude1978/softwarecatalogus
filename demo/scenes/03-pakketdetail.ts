import { Page } from 'playwright';
import { BASE_URL } from '../helpers/config';
import { short, medium, long, waitForStable, scrollIntoView } from '../helpers/timing';
import { showStep, highlightElement } from '../helpers/overlay';

export const name = '03-pakketdetail';
export const title = 'Pakketdetail — Suite4Gemeenten';

// UUID van Suite4Gemeenten in de seed-data
const PAKKET_ID = 'ec8338cf-84bf-4783-9985-fe9af1068bf7';

export async function run(page: Page): Promise<void> {
  await page.goto(`${BASE_URL}/pakketten`);
  await waitForStable(page);

  // Klik op Suite4Gemeenten
  await showStep(
    page,
    6,
    'Pakketdetail openen',
    'Klik op "Suite4Gemeenten" voor de volledige detailpagina.'
  );
  await medium();

  // Probeer via link, anders direct naar ID
  const link = page.locator('a', { hasText: 'Suite4Gemeenten' }).first();
  const exists = await link.count();
  if (exists > 0) {
    await link.click();
  } else {
    await page.goto(`${BASE_URL}/pakketten/${PAKKET_ID}`);
  }
  await waitForStable(page);

  // Stap: Beschrijving
  await showStep(
    page,
    7,
    'Beschrijving & Metadata',
    'Integraal zaaksysteem — SaaS op Microsoft Azure. Gebruikt door 15 gemeenten.'
  );
  await highlightElement(page, 'h1', '#4A90D9', 1500);
  await long(2500);

  // Scroll naar Ondersteunde standaarden
  await showStep(
    page,
    8,
    'Ondersteunde standaarden',
    'Suite4Gemeenten ondersteunt DigiD, StUF-ZKN, ZGW API\'s, HTTPS/HSTS en meer.'
  );
  await scrollIntoView(page, 'text=Ondersteunde standaarden');
  await highlightElement(page, 'text=Ondersteunde standaarden', '#10B981', 1500);
  await long(2500);

  // Scroll naar GEMMA-componenten
  await showStep(
    page,
    9,
    'GEMMA-componenten',
    'Pakket is gekoppeld aan: Zaaksysteem, Zaakregistratieservice, Midoffice.'
  );
  await scrollIntoView(page, 'text=GEMMA component');
  await medium(1800);

  // Scroll naar Gebruikt door
  await showStep(
    page,
    10,
    '"Gebruikt door" — Gluren bij de buren',
    '15 Nederlandse gemeenten gebruiken dit pakket. Klik op een gemeente voor hun volledige pakketlandschap.'
  );
  await scrollIntoView(page, 'text=Gebruikt door');
  await long(2800);

  // Hover over eerste gemeente
  const gemeente = page.locator('text=Gemeente Utrecht').first();
  if (await gemeente.count()) {
    await gemeente.hover();
    await medium();
  }
}
