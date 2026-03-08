/**
 * run-demo.ts — Orkestrator voor de Softwarecatalogus demo-opname
 *
 * Gebruik:
 *   npx ts-node run-demo.ts                        → alle scènes → 1 video
 *   npx ts-node run-demo.ts --scene 03             → één scène opnemen
 *   npx ts-node run-demo.ts --suite gemeente        → 1 van de 4 persona-videos
 *   npx ts-node run-demo.ts --all-suites            → alle 4 persona-videos
 *   npx ts-node run-demo.ts --merge                 → bestaande clips samenvoegen
 *   npx ts-node run-demo.ts --list                  → lijst alle scènes
 *   npx ts-node run-demo.ts --list-suites           → lijst suites
 *
 * Omgevingsvariabelen:
 *   DEMO_BASE_URL   URL van de app (default: http://localhost)
 *   DEMO_SLOW       Timing-factor, bijv. 1.5 = 50% langzamer (default: 1.0)
 */

import * as path from 'path';
import * as fs from 'fs';
import { chromium, Browser, BrowserContext, Page } from 'playwright';
import { VIEWPORT, OUTPUT_DIR } from './helpers/config';
import { injectCursorTracker } from './helpers/overlay';

// ── Scènes importeren ──────────────────────────────────────────────────────────
import * as s01 from './scenes/01-homepage';
import * as s02 from './scenes/02-pakketten';
import * as s03 from './scenes/03-pakketdetail';
import * as s04 from './scenes/04-organisaties';
import * as s05 from './scenes/05-standaarden';
import * as s06 from './scenes/06-login-gemeente';
import * as s07 from './scenes/07-mijn-landschap';
import * as s08 from './scenes/08-logout-gemeente';
import * as s09 from './scenes/09-login-leverancier';
import * as s10 from './scenes/10-aanbod-beheren';
import * as s11 from './scenes/11-login-admin';
import * as s12 from './scenes/12-organisatiebeheer';
import * as s13 from './scenes/13-gemma-beheer';
import * as s14 from './scenes/14-ameff-import';
import * as s15 from './scenes/15-api-swagger';
import * as s16 from './scenes/16-api-live';

type Scene = { name: string; title: string; run: (page: Page) => Promise<void> };

const ALL_SCENES: Scene[] = [
  s01, s02, s03, s04, s05,
  s06, s07, s08,
  s09, s10,
  s11, s12, s13, s14,
  s15, s16,
];

// ── Suites (persona-gerichte video's) ─────────────────────────────────────────

const SUITES: Record<string, { titel: string; omschrijving: string; scenes: Scene[]; output: string }> = {
  publiek: {
    titel:       'Deel A — Publieke catalogus',
    omschrijving: 'Homepage, pakketten zoeken & filteren, pakketdetail, organisaties, standaarden',
    scenes:      [s01, s02, s03, s04, s05],
    output:      'swc-demo-publiek.mp4',
  },
  gemeente: {
    titel:       'Deel B — Gemeente gebruik-beheerder',
    omschrijving: 'Inloggen als Jan Jansen (Utrecht), mijn pakketlandschap, uitloggen',
    scenes:      [s06, s07, s08],
    output:      'swc-demo-gemeente.mp4',
  },
  leverancier: {
    titel:       'Deel C — Leverancier aanbod-beheerder',
    omschrijving: 'Inloggen als Centric, pakketaanbod beheren en concept-status patroon',
    scenes:      [s09, s10],
    output:      'swc-demo-leverancier.mp4',
  },
  vng: {
    titel:       'Deel D+E — VNG Realisatie functioneel beheerder & API',
    omschrijving: 'Organisatiebeheer, GEMMA ArchiMate, AMEFF-import, Swagger, live API',
    scenes:      [s11, s12, s13, s14, s15, s16],
    output:      'swc-demo-vng.mp4',
  },
};

// ── Helpers ────────────────────────────────────────────────────────────────────

function log(msg: string) {
  const ts = new Date().toLocaleTimeString('nl-NL');
  console.log(`[${ts}] ${msg}`);
}

function ensureDir(dir: string) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

// ── Scène opnemen ──────────────────────────────────────────────────────────────

async function recordScene(browser: Browser, scene: Scene): Promise<string> {
  const clipDir = path.resolve(OUTPUT_DIR, scene.name);
  ensureDir(clipDir);

  const context: BrowserContext = await browser.newContext({
    viewport: VIEWPORT,
    recordVideo: { dir: clipDir, size: VIEWPORT },
    locale: 'nl-NL',
    timezoneId: 'Europe/Amsterdam',
  });

  const page: Page = await context.newPage();

  // Cursor-tracker: volgt elke muisbeweging met een rode stip (zichtbaar in video)
  await injectCursorTracker(page);

  log(`▶ Scène: ${scene.name} — "${scene.title}"`);
  try {
    await scene.run(page);
    log(`✓ Klaar: ${scene.name}`);
  } catch (err) {
    log(`✗ Fout in ${scene.name}: ${(err as Error).message}`);
  }

  await context.close(); // slaat video op

  const files = fs.readdirSync(clipDir).filter((f) => f.endsWith('.webm'));
  if (files.length === 0) throw new Error(`Geen video gevonden in ${clipDir}`);

  const src = path.join(clipDir, files[0]);
  const dst = path.resolve(OUTPUT_DIR, `${scene.name}.webm`);
  fs.renameSync(src, dst);
  fs.rmSync(clipDir, { recursive: true, force: true });

  log(`  📹 ${path.basename(dst)}`);
  return dst;
}

// ── Clips samenvoegen ──────────────────────────────────────────────────────────

async function mergeClips(clips: string[], outputFile: string): Promise<void> {
  const { execSync } = await import('child_process');
  const listFile = path.resolve(OUTPUT_DIR, 'concat-list.txt');

  const content = clips.map((c) => `file '${c.replace(/\\/g, '/')}'`).join('\n');
  fs.writeFileSync(listFile, content, 'utf-8');

  log(`🎬 Samenvoegen van ${clips.length} clip(s) → ${path.basename(outputFile)}`);
  try {
    execSync(
      `ffmpeg -y -f concat -safe 0 -i "${listFile}" -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p "${outputFile}"`,
      { stdio: 'inherit' }
    );
    log(`✅ Video klaar: ${outputFile}`);
  } catch {
    log('⚠  ffmpeg niet gevonden of fout — clips staan los in output/clips/');
    log(`   Handmatig: ffmpeg -f concat -safe 0 -i "${listFile}" -c:v libx264 "${outputFile}"`);
  }

  if (fs.existsSync(listFile)) fs.unlinkSync(listFile);
}

// ── Opname-run ─────────────────────────────────────────────────────────────────

async function runScenes(
  browser: Browser,
  scenes: Scene[],
  outputFile: string
): Promise<void> {
  const clips: string[] = [];

  for (const scene of scenes) {
    const clip = await recordScene(browser, scene);
    clips.push(clip);
  }

  if (clips.length > 1) {
    await mergeClips(clips, outputFile);
  } else if (clips.length === 1) {
    log(`📹 Losse clip (geen merge nodig): ${clips[0]}`);
  }
}

// ── Main ───────────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);

  // --list
  if (args.includes('--list')) {
    console.log('\nBeschikbare scènes:');
    ALL_SCENES.forEach((s, i) =>
      console.log(`  ${String(i + 1).padStart(2, '0')}  ${s.name.padEnd(32)} ${s.title}`)
    );
    return;
  }

  // --list-suites
  if (args.includes('--list-suites')) {
    console.log('\nBeschikbare suites (persona-video\'s):');
    Object.entries(SUITES).forEach(([key, s]) => {
      console.log(`\n  --suite ${key}`);
      console.log(`    ${s.titel}`);
      console.log(`    ${s.omschrijving}`);
      console.log(`    Output: output/${s.output}`);
      console.log(`    Scènes: ${s.scenes.map((sc) => sc.name).join(', ')}`);
    });
    return;
  }

  // --merge  →  voeg bestaande clips samen (geen nieuwe opname)
  if (args.includes('--merge')) {
    const suiteArg = args[args.indexOf('--suite') + 1];
    let outputFile: string;
    let clips: string[];

    if (suiteArg && SUITES[suiteArg]) {
      const suite = SUITES[suiteArg];
      clips = suite.scenes
        .map((s) => path.resolve(OUTPUT_DIR, `${s.name}.webm`))
        .filter((f) => fs.existsSync(f));
      outputFile = path.resolve(OUTPUT_DIR, '..', suite.output);
      log(`🔀 Merge suite "${suiteArg}": ${clips.length} clip(s)`);
    } else {
      const clipsDir = path.resolve(OUTPUT_DIR);
      if (!fs.existsSync(clipsDir)) {
        console.error(`Geen clips-map gevonden: ${clipsDir}`);
        process.exit(1);
      }
      clips = fs
        .readdirSync(clipsDir)
        .filter((f) => f.endsWith('.webm'))
        .sort()
        .map((f) => path.join(clipsDir, f));
      outputFile = path.resolve(OUTPUT_DIR, '..', 'softwarecatalogus-demo.mp4');
    }

    if (clips.length === 0) {
      console.error('Geen .webm-bestanden gevonden.');
      process.exit(1);
    }
    clips.forEach((c) => log(`   ${path.basename(c)}`));
    await mergeClips(clips, outputFile);
    log('🏁 Klaar!');
    return;
  }

  ensureDir(OUTPUT_DIR);

  const browser: Browser = await chromium.launch({
    headless: false,
    args: ['--disable-infobars', '--no-sandbox'],
  });

  // --all-suites  →  4 afzonderlijke persona-video's
  if (args.includes('--all-suites')) {
    log('🚀 Alle suites opnemen (4 persona-video\'s)');
    for (const [key, suite] of Object.entries(SUITES)) {
      log(`\n━━━━ Suite: ${key} — ${suite.titel} ━━━━`);
      const outputFile = path.resolve(OUTPUT_DIR, '..', suite.output);
      await runScenes(browser, suite.scenes, outputFile);
    }
    await browser.close();
    log('\n🏁 Alle suites klaar!');
    return;
  }

  // --suite gemeente  /  --suite vng  etc.
  const suiteArg = args[args.indexOf('--suite') + 1];
  if (suiteArg) {
    const suite = SUITES[suiteArg];
    if (!suite) {
      console.error(`Suite niet gevonden: "${suiteArg}". Kies uit: ${Object.keys(SUITES).join(', ')}`);
      process.exit(1);
    }
    log(`🚀 Suite: ${suite.titel}`);
    log(`   ${suite.scenes.length} scène(s) → output/${suite.output}`);
    const outputFile = path.resolve(OUTPUT_DIR, '..', suite.output);
    await runScenes(browser, suite.scenes, outputFile);
    await browser.close();
    log('🏁 Klaar!');
    return;
  }

  // --scene 03  of  --scene 03-pakketdetail
  const sceneArg = args[args.indexOf('--scene') + 1];
  let scenesToRun = ALL_SCENES;
  if (sceneArg) {
    scenesToRun = ALL_SCENES.filter((s) => s.name.startsWith(sceneArg));
    if (scenesToRun.length === 0) {
      console.error(`Scène niet gevonden: ${sceneArg}`);
      process.exit(1);
    }
  }

  log('🚀 Softwarecatalogus demo-opname gestart');
  log(`   ${scenesToRun.length} scène(s)  |  Viewport: ${VIEWPORT.width}×${VIEWPORT.height}`);

  const outputFile = path.resolve(OUTPUT_DIR, '..', 'softwarecatalogus-demo.mp4');
  await runScenes(browser, scenesToRun, outputFile);
  await browser.close();
  log('🏁 Klaar!');
}

main().catch((err) => {
  console.error('Fatale fout:', err);
  process.exit(1);
});
