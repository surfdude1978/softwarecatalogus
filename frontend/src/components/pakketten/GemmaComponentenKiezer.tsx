"use client";

import { useState, useMemo } from "react";
import { Search, X } from "lucide-react";
import { useGemmaComponenten } from "@/hooks/use-pakketten-beheer";
import type { GemmaComponent } from "@/types";

// ── Type-labels ───────────────────────────────────────────────────────────────

const TYPE_LABEL: Record<GemmaComponent["type"], string> = {
  applicatiecomponent: "Applicatiecomponent",
  applicatieservice: "Applicatieservice",
  applicatiefunctie: "Applicatiefunctie",
  anders: "Anders",
};

// Volgorde van weergave
const TYPE_VOLGORDE: GemmaComponent["type"][] = [
  "applicatiecomponent",
  "applicatieservice",
  "applicatiefunctie",
  "anders",
];

// ── Props ─────────────────────────────────────────────────────────────────────

interface GemmaComponentenKiezerProps {
  /** Geselecteerde GEMMA-component IDs */
  value: string[];
  /** Callback bij wijziging van de selectie */
  onChange: (ids: string[]) => void;
  /** Optionele foutmelding */
  error?: string;
  /** Toon skeleton-loader terwijl componenten laden */
  isLoading?: boolean;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function GemmaComponentenKiezer({
  value,
  onChange,
  error,
}: GemmaComponentenKiezerProps) {
  const [zoekTerm, setZoekTerm] = useState("");
  const { data, isLoading, isError } = useGemmaComponenten();

  // data is een gewone array (pagination_class=None op de backend)
  const alleComponenten = data ?? [];

  // Filter op zoekterm
  const gefilterd = useMemo(() => {
    if (!zoekTerm.trim()) return alleComponenten;
    const q = zoekTerm.toLowerCase();
    return alleComponenten.filter(
      (c) =>
        c.naam.toLowerCase().includes(q) ||
        c.archimate_id.toLowerCase().includes(q) ||
        c.beschrijving?.toLowerCase().includes(q)
    );
  }, [alleComponenten, zoekTerm]);

  // Groepeer per type
  const groepen = useMemo(() => {
    const map = new Map<GemmaComponent["type"], GemmaComponent[]>();
    for (const c of gefilterd) {
      if (!map.has(c.type)) map.set(c.type, []);
      map.get(c.type)!.push(c);
    }
    return TYPE_VOLGORDE.filter((t) => map.has(t)).map((t) => ({
      type: t,
      label: TYPE_LABEL[t],
      componenten: map.get(t)!,
    }));
  }, [gefilterd]);

  function toggle(id: string) {
    if (value.includes(id)) {
      onChange(value.filter((v) => v !== id));
    } else {
      onChange([...value, id]);
    }
  }

  // Haal namen van geselecteerde componenten op voor de badgelabels
  const geselecteerdeNamen = useMemo(() => {
    return alleComponenten
      .filter((c) => value.includes(c.id))
      .map((c) => ({ id: c.id, naam: c.naam }));
  }, [alleComponenten, value]);

  // ── Laadstatus ──────────────────────────────────────────────────────────────

  if (isLoading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-8 animate-pulse rounded-md bg-gray-100" />
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <p className="text-sm text-red-600">
        Kon GEMMA-componenten niet laden. Probeer de pagina te vernieuwen.
      </p>
    );
  }

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div className="space-y-3">
      {/* Geselecteerde badges */}
      {geselecteerdeNamen.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {geselecteerdeNamen.map(({ id, naam }) => (
            <span
              key={id}
              className="inline-flex items-center gap-1 rounded-full bg-primary-100 px-2.5 py-0.5 text-xs font-medium text-primary-800"
            >
              {naam}
              <button
                type="button"
                onClick={() => toggle(id)}
                className="ml-0.5 rounded-full hover:bg-primary-200"
                aria-label={`Verwijder ${naam}`}
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Zoekbalk */}
      <div className="relative">
        <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-gray-400" />
        <input
          type="search"
          value={zoekTerm}
          onChange={(e) => setZoekTerm(e.target.value)}
          placeholder="Zoek GEMMA-component…"
          className="w-full rounded-md border border-gray-200 bg-gray-50 py-1.5 pl-8 pr-3 text-xs placeholder-gray-400 focus:border-primary-400 focus:bg-white focus:outline-none focus:ring-1 focus:ring-primary-400"
        />
      </div>

      {/* Componentlijst */}
      <div className="max-h-64 overflow-y-auto rounded-md border border-gray-200 bg-white">
        {groepen.length === 0 ? (
          <p className="px-3 py-4 text-center text-xs text-gray-400">
            Geen componenten gevonden{zoekTerm ? ` voor "${zoekTerm}"` : ""}.
          </p>
        ) : (
          groepen.map((groep) => (
            <div key={groep.type}>
              {/* Groepheader */}
              <div className="sticky top-0 bg-gray-50 px-3 py-1.5">
                <span className="text-[10px] font-semibold uppercase tracking-wide text-gray-500">
                  {groep.label}
                </span>
              </div>
              {/* Component-checkboxen */}
              {groep.componenten.map((comp) => {
                const geselecteerd = value.includes(comp.id);
                return (
                  <label
                    key={comp.id}
                    className={`flex cursor-pointer items-start gap-2.5 px-3 py-2 hover:bg-gray-50 ${
                      geselecteerd ? "bg-primary-50" : ""
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={geselecteerd}
                      onChange={() => toggle(comp.id)}
                      className="mt-0.5 h-3.5 w-3.5 shrink-0 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <div className="min-w-0">
                      <p className="text-xs font-medium text-gray-800 leading-tight">
                        {comp.naam}
                      </p>
                      <p className="text-[10px] text-gray-400 font-mono">
                        {comp.archimate_id}
                      </p>
                    </div>
                  </label>
                );
              })}
            </div>
          ))
        )}
      </div>

      {/* Teller */}
      <p className="text-[11px] text-gray-400">
        {value.length === 0
          ? "Geen componenten geselecteerd"
          : `${value.length} component${value.length !== 1 ? "en" : ""} geselecteerd`}
      </p>

      {/* Foutmelding */}
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}
