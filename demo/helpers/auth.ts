import { Page } from 'playwright';
import { BASE_URL, ACCOUNTS } from './config';

// ─── Auth helpers ──────────────────────────────────────────────────────────────

type Rol = keyof typeof ACCOUNTS;

/**
 * Log in via de API en sla tokens op in localStorage.
 *
 * Navigeert NIET naar /login — dat veroorzaakte een zichtbare login-flash
 * in scènes waar de gebruiker al ingelogd hoort te zijn.
 * Het DRF JWT-endpoint vereist geen CSRF-token (geen session auth).
 *
 * Voor scènes die de login-pagina bewust tonen (06, 09, 11) werkt dit ook:
 * die navigeren zelf al naar /login, en loginApi hoeft de pagina dan niet
 * te verlaten — de tokens worden op de huidige origin opgeslagen.
 */
export async function loginApi(page: Page, rol: Rol): Promise<void> {
  const account = ACCOUNTS[rol];

  // Zorg dat we op de app-origin staan zodat fetch en localStorage bereikbaar zijn.
  // Navigeer naar / — NIET naar /login — om de login-flash te vermijden.
  if (!page.url().startsWith(BASE_URL)) {
    await page.goto(`${BASE_URL}/`);
    await page.waitForLoadState('domcontentloaded');
  }

  const token = await page.evaluate(async (creds) => {
    // JWT-login — geen CSRF nodig (DRF JWTAuthentication vereist dat niet)
    const res = await fetch('/api/v1/auth/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: creds.email, password: creds.password }),
    });

    const data = await res.json() as Record<string, unknown>;
    const access = (data['access_token'] ?? data['access']) as string | undefined;
    const refresh = (data['refresh_token'] ?? data['refresh']) as string | undefined;
    if (access) {
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh ?? '');
    }
    return { access, status: res.status, keys: Object.keys(data) };
  }, { email: account.email, password: account.password });

  if (!token.access) {
    throw new Error(
      `Login mislukt voor ${rol} (${account.email}) — ` +
      `HTTP ${token.status}, response-velden: ${(token as { keys?: string[] }).keys?.join(', ') ?? '?'}`
    );
  }
  // Tokens staan nu in localStorage. De aanroepende scène navigeert zelf
  // naar de gewenste pagina; React leest de tokens bij mount automatisch op.
}

/** Logout: verwijder tokens en ga naar /login */
export async function logout(page: Page): Promise<void> {
  // Zorg dat de pagina op de app-origin staat voor localStorage-toegang
  try {
    if (!page.url().startsWith(BASE_URL)) {
      await page.goto(`${BASE_URL}/`);
      await page.waitForLoadState('domcontentloaded');
    }
    await page.evaluate(() => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    });
  } catch {
    // localStorage niet toegankelijk (bijv. about:blank) — doorgaan met navigatie
  }
  await page.goto(`${BASE_URL}/login`);
  await page.waitForLoadState('networkidle');
}

/** Selecteer in een <select> via React-native setter */
export async function selectOption(page: Page, selector: string, value: string): Promise<void> {
  await page.evaluate(
    ({ selector, value }) => {
      const sel = document.querySelector(selector) as HTMLSelectElement | null;
      if (!sel) return;
      const nativeSetter = Object.getOwnPropertyDescriptor(
        window.HTMLSelectElement.prototype,
        'value'
      )!.set!;
      nativeSetter.call(sel, value);
      sel.dispatchEvent(new Event('change', { bubbles: true }));
    },
    { selector, value }
  );
}

/** Vul een React-input via native setter (triggert onChange) */
export async function fillReact(page: Page, selector: string, value: string): Promise<void> {
  await page.evaluate(
    ({ selector, value }) => {
      const inp = document.querySelector(selector) as HTMLInputElement | null;
      if (!inp) return;
      const nativeSetter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype,
        'value'
      )!.set!;
      nativeSetter.call(inp, value);
      inp.dispatchEvent(new Event('input', { bubbles: true }));
    },
    { selector, value }
  );
}
