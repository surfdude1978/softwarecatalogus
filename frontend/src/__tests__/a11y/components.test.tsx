/**
 * Toegankelijkheidstest (WCAG 2.1 AA) met jest-axe.
 * Controleert automatisch op veelvoorkomende toegankelijkheidsproblemen.
 */
import React from "react";
import { render } from "@testing-library/react";
import { axe, toHaveNoViolations } from "jest-axe";

expect.extend(toHaveNoViolations);

// ── UI Componenten ─────────────────────────────────────────────────────────

import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Select } from "@/components/ui/Select";
import { Badge } from "@/components/ui/Badge";

describe("Input component — WCAG 2.1 AA", () => {
  it("heeft geen toegankelijkheidsovertredingen", async () => {
    const { container } = render(
      <Input id="naam" label="Volledige naam" placeholder="Jan de Vries" />
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it("heeft geen overtredingen met foutmelding", async () => {
    const { container } = render(
      <Input
        id="email"
        label="E-mailadres"
        type="email"
        error="Vul een geldig e-mailadres in."
      />
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

describe("Button component — WCAG 2.1 AA", () => {
  it("heeft geen toegankelijkheidsovertredingen (primair)", async () => {
    const { container } = render(
      <Button onClick={() => {}}>Opslaan</Button>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it("heeft geen overtredingen (uitgeschakeld)", async () => {
    const { container } = render(
      <Button disabled aria-label="Opslaan — niet beschikbaar">
        Opslaan
      </Button>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

describe("Select component — WCAG 2.1 AA", () => {
  const opties = [
    { value: "gemeente", label: "Gemeente" },
    { value: "leverancier", label: "Leverancier" },
  ];

  it("heeft geen toegankelijkheidsovertredingen", async () => {
    const { container } = render(
      <Select
        id="type"
        label="Organisatietype"
        options={opties}
        value="gemeente"
        onChange={() => {}}
      />
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it("heeft geen overtredingen met foutmelding", async () => {
    const { container } = render(
      <Select
        id="type-err"
        label="Organisatietype"
        options={opties}
        value=""
        onChange={() => {}}
        error="Selecteer een organisatietype."
      />
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

describe("Badge component — WCAG 2.1 AA", () => {
  it("heeft geen toegankelijkheidsovertredingen", async () => {
    const { container } = render(<Badge variant="info">Actief</Badge>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

// ── Formulieren ─────────────────────────────────────────────────────────────

describe("Zoekformulier — WCAG 2.1 AA", () => {
  it("heeft geen overtredingen bij zoekbalk met role=search", async () => {
    const { container } = render(
      <form role="search">
        <label htmlFor="zoek" className="sr-only">
          Zoeken in de catalogus
        </label>
        <input
          id="zoek"
          type="search"
          aria-label="Zoeken in de catalogus"
          placeholder="Zoek pakketten..."
        />
        <button type="submit">Zoeken</button>
      </form>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

// ── Navigatie ─────────────────────────────────────────────────────────────

describe("Navigatie — WCAG 2.1 AA", () => {
  it("hoofdnavigatie met aria-label heeft geen overtredingen", async () => {
    const { container } = render(
      <nav aria-label="Hoofdnavigatie">
        <a href="/" aria-label="Softwarecatalogus — Startpagina">
          Softwarecatalogus
        </a>
        <a href="/pakketten" aria-current="page">
          Pakketten
        </a>
        <a href="/organisaties">Organisaties</a>
      </nav>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it("skip-to-content link heeft geen overtredingen", async () => {
    const { container } = render(
      <div>
        <a href="#main-content">Ga naar hoofdinhoud</a>
        <nav aria-label="Hoofdnavigatie">
          <a href="/pakketten">Pakketten</a>
        </nav>
        <main id="main-content" tabIndex={-1}>
          <h1>Pakketten</h1>
        </main>
      </div>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
