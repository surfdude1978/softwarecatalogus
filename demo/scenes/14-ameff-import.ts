import * as fs from 'fs';
import * as path from 'path';
import { Page } from 'playwright';
import { BASE_URL } from '../helpers/config';
import { short, medium, long, waitForStable } from '../helpers/timing';
import { showStep } from '../helpers/overlay';
import { loginApi } from '../helpers/auth';

export const name = '14-ameff-import';
export const title = 'AMEFF-import — demo';

/** Minimaal geldig AMEFF XML-bestand voor de demo */
const DEMO_AMEFF = `<?xml version="1.0" encoding="UTF-8"?>
<model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.opengroup.org/xsd/archimate/3.0/ http://www.opengroup.org/xsd/archimate/3.0/archimate3_Diagram.xsd"
       identifier="model-demo-001">
  <name xml:lang="nl">GEMMA Demo Import</name>
  <elements>
    <element identifier="GEMMA-AC-DEMO" xsi:type="ApplicationComponent">
      <name xml:lang="nl">Demo Applicatiecomponent</name>
      <documentation xml:lang="nl">Tijdelijke demo-component voor AMEFF-importdemonstratie.</documentation>
    </element>
  </elements>
</model>`;

export async function run(page: Page): Promise<void> {
  // Schrijf demo AMEFF naar assets-map
  const ameffPath = path.resolve(__dirname, '../assets/demo-import.xml');
  fs.writeFileSync(ameffPath, DEMO_AMEFF, 'utf-8');

  // Verse context — stil inloggen als admin
  await loginApi(page, 'admin');
  await page.goto(`${BASE_URL}/beheer/gemma`);
  await waitForStable(page);

  await showStep(
    page,
    29,
    'AMEFF-import uitvoeren',
    'Upload een ArchiMate XML-bestand. Het systeem parseert de componenten en voegt ze toe aan de catalogus.'
  );
  await medium(1500);

  // Selecteer het demo-bestand
  const fileInput = page.locator('input[type="file"]').first();
  if (await fileInput.count()) {
    await fileInput.setInputFiles(ameffPath);
    await short(800);

    await showStep(
      page,
      30,
      'Bestand geselecteerd',
      `demo-import.xml (${DEMO_AMEFF.length} bytes) klaar voor upload. Klik "Importeren" om te verwerken.`
    );
    await medium(2000);

    // Hover over de importeer-knop (niet klikken in demo — voorkomt side-effects)
    const importBtn = page.locator('button:has-text("Importeren")').first();
    if (await importBtn.count()) {
      await importBtn.hover();
      await long(2000);
    }
  } else {
    await showStep(page, 30, 'AMEFF Upload', 'Kies een bestand via de bestandskiezer en klik "Importeren".');
    await long(2000);
  }
}
