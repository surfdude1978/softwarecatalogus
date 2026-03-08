import { Page } from 'playwright';

// ─── On-screen annotaties ──────────────────────────────────────────────────────
// Annotaties zijn gepositioneerd onderin het midden (bottom-center):
//   • Nooit geraakt door browser-chrome of navigatiebalk
//   • Altijd volledig zichtbaar ongeacht viewport-breedte
//   • Kijker hoeft ogen niet van het centrale content af te halen

// ── Cursor tracker ─────────────────────────────────────────────────────────────

/**
 * Injecteer een rode cursor-indicator die de muisbeweging volgt.
 * Gebruik page.addInitScript zodat hij bij elke navigatie opnieuw wordt ingeladen.
 */
export async function injectCursorTracker(page: Page): Promise<void> {
  await page.addInitScript(() => {
    const ID = '__demo_cursor';
    window.addEventListener('mousemove', (e) => {
      let el = document.getElementById(ID);
      if (!el) {
        el = document.createElement('div');
        el.id = ID;
        el.style.cssText = [
          'position:fixed',
          'width:26px',
          'height:26px',
          'background:rgba(239,68,68,0.85)',
          'border:3px solid rgba(255,255,255,0.95)',
          'border-radius:50%',
          'pointer-events:none',
          'z-index:2147483647',
          'transform:translate(-50%,-50%)',
          'box-shadow:0 0 0 3px rgba(239,68,68,0.3),0 3px 14px rgba(0,0,0,0.45)',
        ].join(';');
        (document.body ?? document.documentElement).appendChild(el);
      }
      el.style.left = e.clientX + 'px';
      el.style.top  = e.clientY + 'px';
    });
  });
}

// ── Stap-annotatie (bottom-center) ─────────────────────────────────────────────

/** Toon een stap-annotatie onderin het midden */
export async function showStep(
  page: Page,
  stap: number,
  titel: string,
  omschrijving: string
): Promise<void> {
  await page.evaluate(
    ({ stap, titel, omschrijving }) => {
      document.getElementById('__demo_ann')?.remove();
      const el = document.createElement('div');
      el.id = '__demo_ann';
      el.style.cssText = [
        'position:fixed',
        'bottom:28px',
        'left:50%',
        'transform:translateX(-50%)',
        'background:rgba(14,48,87,0.97)',
        'color:#fff',
        'padding:14px 22px',
        'border-radius:12px',
        'font-family:Arial,sans-serif',
        'font-size:14px',
        'max-width:560px',
        'width:max-content',
        'z-index:2147483647',
        'box-shadow:0 6px 28px rgba(0,0,0,.55)',
        'border-top:3px solid #4A90D9',
        'line-height:1.55',
        'pointer-events:none',
        'white-space:normal',
        'word-break:break-word',
      ].join(';');
      el.innerHTML =
        `<div style="font-size:10px;opacity:.55;margin-bottom:5px;letter-spacing:1.1px;text-transform:uppercase;text-align:center">▶ Stap ${stap}</div>` +
        `<div style="font-weight:700;font-size:15px;margin-bottom:6px;text-align:center">${titel}</div>` +
        `<div style="opacity:.88;font-size:13px;text-align:center">${omschrijving}</div>`;
      document.body.appendChild(el);
    },
    { stap, titel, omschrijving }
  );
}

/** Verwijder annotatie (fade-out) */
export async function hideStep(page: Page): Promise<void> {
  await page.evaluate(() => {
    const el = document.getElementById('__demo_ann');
    if (el) {
      el.style.transition = 'opacity .3s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 320);
    }
  });
}

// ── Hoofdstuktitel (full-screen overlay) ───────────────────────────────────────

/** Toon een hoofdstuktitel als full-screen overlay */
export async function showChapterTitle(
  page: Page,
  hoofdstuk: string,
  ondertitel = ''
): Promise<void> {
  await page.evaluate(
    ({ hoofdstuk, ondertitel }) => {
      document.getElementById('__demo_chapter')?.remove();
      const el = document.createElement('div');
      el.id = '__demo_chapter';
      el.style.cssText = [
        'position:fixed',
        'inset:0',
        'background:rgba(8,20,40,0.96)',
        'color:#fff',
        'display:flex',
        'flex-direction:column',
        'align-items:center',
        'justify-content:center',
        'gap:12px',
        'z-index:2147483646',
        'font-family:Arial,sans-serif',
        'pointer-events:none',
      ].join(';');
      el.innerHTML =
        `<div style="font-size:12px;letter-spacing:2.5px;opacity:.45;text-transform:uppercase;margin-bottom:8px">Softwarecatalogus — Demo</div>` +
        `<div style="font-size:40px;font-weight:700;text-align:center;line-height:1.2">${hoofdstuk}</div>` +
        (ondertitel
          ? `<div style="font-size:17px;opacity:.65;text-align:center;margin-top:6px">${ondertitel}</div>`
          : '');
      document.body.appendChild(el);
    },
    { hoofdstuk, ondertitel }
  );
}

/** Verwijder hoofdstuktitel */
export async function hideChapterTitle(page: Page): Promise<void> {
  await page.evaluate(() => {
    const el = document.getElementById('__demo_chapter');
    if (el) {
      el.style.transition = 'opacity .45s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 470);
    }
  });
}

// ── Highlight ───────────────────────────────────────────────────────────────────

/** Highlight een element met een gekleurde rand (tijdelijk) */
export async function highlightElement(
  page: Page,
  selector: string,
  color = '#4A90D9',
  durationMs = 2000
): Promise<void> {
  try {
    await page.locator(selector).first().evaluate(
      (el, args) => {
        const htmlEl = el as HTMLElement;
        const origOutline = htmlEl.style.outline;
        const origOffset  = htmlEl.style.outlineOffset;
        const origShadow  = htmlEl.style.boxShadow;
        htmlEl.style.outline      = `3px solid ${args.color}`;
        htmlEl.style.outlineOffset = '4px';
        htmlEl.style.boxShadow    = `0 0 0 6px ${args.color}33`;
        setTimeout(() => {
          htmlEl.style.outline      = origOutline;
          htmlEl.style.outlineOffset = origOffset;
          htmlEl.style.boxShadow    = origShadow;
        }, args.durationMs);
      },
      { color, durationMs }
    );
  } catch {
    // Element niet gevonden — sla highlight over
  }
}
