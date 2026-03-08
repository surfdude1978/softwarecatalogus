"use client";

import { useState } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import type { KaartComponent, KaartPakket } from "@/hooks/use-gemma";

// ─── Kleur & stijl hulpfuncties ───────────────────────────────────────────────

const STATUS_KLEUR: Record<string, string> = {
  in_gebruik:
    "bg-green-100 text-green-800 border border-green-200 hover:bg-green-200",
  gepland:
    "bg-yellow-100 text-yellow-800 border border-yellow-200 hover:bg-yellow-200",
  gestopt:
    "bg-gray-100 text-gray-600 border border-gray-200 hover:bg-gray-200",
};

const STATUS_LABEL: Record<string, string> = {
  in_gebruik: "In gebruik",
  gepland: "Gepland",
  gestopt: "Gestopt",
};

const TYPE_ICOON: Record<string, string> = {
  applicatiecomponent: "□",
  applicatieservice: "◇",
  applicatiefunctie: "○",
  anders: "·",
};

const NIVEAU_STIJL = [
  // Niveau 0 — root
  "border-2 border-primary-200 bg-primary-50",
  // Niveau 1
  "border border-gray-300 bg-white",
  // Niveau 2+
  "border border-gray-200 bg-gray-50",
];

// ─── PakketBadge ─────────────────────────────────────────────────────────────

function PakketBadge({ pakket }: { pakket: KaartPakket }) {
  const kleur =
    pakket.status_gebruik
      ? STATUS_KLEUR[pakket.status_gebruik] ?? STATUS_KLEUR.in_gebruik
      : "bg-blue-100 text-blue-800 border border-blue-200 hover:bg-blue-200";

  return (
    <Link
      href={`/pakketten/${pakket.id}`}
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs transition-colors",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500",
        kleur
      )}
      title={
        pakket.leverancier_naam
          ? `${pakket.leverancier_naam}${pakket.status_gebruik ? ` — ${STATUS_LABEL[pakket.status_gebruik]}` : ""}`
          : undefined
      }
    >
      <span className="max-w-[14ch] truncate">{pakket.naam}</span>
      {pakket.status_gebruik && (
        <span
          aria-label={STATUS_LABEL[pakket.status_gebruik]}
          className={cn(
            "h-1.5 w-1.5 rounded-full shrink-0",
            pakket.status_gebruik === "in_gebruik" && "bg-green-500",
            pakket.status_gebruik === "gepland" && "bg-yellow-500",
            pakket.status_gebruik === "gestopt" && "bg-gray-400"
          )}
        />
      )}
    </Link>
  );
}

// ─── GemmaComponentCard ───────────────────────────────────────────────────────

interface GemmaComponentCardProps {
  component: KaartComponent;
  niveau?: number;
}

function GemmaComponentCard({ component, niveau = 0 }: GemmaComponentCardProps) {
  const [uitgevouwen, setUitgevouwen] = useState(niveau < 1);

  const heeftKinderen = component.kinderen.length > 0;
  const heeftPakketten = component.pakketten.length > 0;
  const niveauKlasse = NIVEAU_STIJL[Math.min(niveau, NIVEAU_STIJL.length - 1)];

  return (
    <div
      className={cn("rounded-lg p-3 transition-all", niveauKlasse)}
      role="region"
      aria-label={component.naam}
    >
      {/* Component header */}
      <div className="flex items-start gap-2">
        {heeftKinderen && (
          <button
            type="button"
            aria-expanded={uitgevouwen}
            aria-label={uitgevouwen ? `${component.naam} inklappen` : `${component.naam} uitvouwen`}
            onClick={() => setUitgevouwen((v) => !v)}
            className="mt-0.5 shrink-0 text-gray-400 hover:text-gray-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 rounded"
          >
            <span aria-hidden="true" className="text-xs leading-none">
              {uitgevouwen ? "▼" : "▶"}
            </span>
          </button>
        )}

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5">
            <span aria-hidden="true" className="text-gray-400 text-sm">
              {TYPE_ICOON[component.type] ?? "·"}
            </span>
            <h3
              className={cn(
                "font-medium text-gray-900 truncate",
                niveau === 0 ? "text-sm" : "text-xs"
              )}
            >
              {component.naam}
            </h3>
            <span className="text-xs text-gray-400 whitespace-nowrap">
              {component.type_display}
            </span>
            {component.gemma_online_url && (
              <a
                href={component.gemma_online_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-primary-500 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 rounded"
                aria-label={`${component.naam} op GEMMA Online (opent in nieuw tabblad)`}
              >
                GEMMA Online ↗
              </a>
            )}
          </div>

          {component.beschrijving && niveau === 0 && (
            <p className="mt-0.5 text-xs text-gray-500 line-clamp-2">
              {component.beschrijving}
            </p>
          )}

          {/* Pakketten */}
          {heeftPakketten && (
            <div className="mt-2 flex flex-wrap gap-1" aria-label="Pakketten">
              {component.pakketten.map((p) => (
                <PakketBadge key={p.id} pakket={p} />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Kinderen */}
      {heeftKinderen && uitgevouwen && (
        <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-3">
          {component.kinderen.map((kind) => (
            <GemmaComponentCard
              key={kind.id}
              component={kind}
              niveau={niveau + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Legenda ─────────────────────────────────────────────────────────────────

function Legenda() {
  return (
    <div
      role="complementary"
      aria-label="Legenda pakketstatus"
      className="flex flex-wrap gap-3 rounded-md border border-gray-200 bg-white p-3 text-xs"
    >
      <span className="font-medium text-gray-700">Legenda:</span>
      {[
        { status: "in_gebruik", label: "In gebruik", kleur: "bg-green-500" },
        { status: "gepland", label: "Gepland", kleur: "bg-yellow-500" },
        { status: "gestopt", label: "Gestopt", kleur: "bg-gray-400" },
        { status: null, label: "Overig actief pakket", kleur: "bg-blue-400" },
      ].map(({ label, kleur }) => (
        <span key={label} className="flex items-center gap-1.5 text-gray-600">
          <span className={cn("h-2 w-2 rounded-full shrink-0", kleur)} aria-hidden="true" />
          {label}
        </span>
      ))}
    </div>
  );
}

// ─── GemmaKaart (hoofd-export) ────────────────────────────────────────────────

interface GemmaKaartProps {
  componenten: KaartComponent[];
  /** Toon de legenda (standaard: true) */
  metLegenda?: boolean;
}

export function GemmaKaart({ componenten, metLegenda = true }: GemmaKaartProps) {
  if (componenten.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center">
        <p className="text-sm text-gray-500">
          Geen GEMMA-componenten gevonden. Importeer eerst een AMEFF-bestand via{" "}
          <Link href="/beheer/gemma" className="text-primary-500 hover:underline">
            GEMMA beheer
          </Link>
          .
        </p>
      </div>
    );
  }

  return (
    <section aria-label="GEMMA architectuurkaart">
      {metLegenda && (
        <div className="mb-4">
          <Legenda />
        </div>
      )}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {componenten.map((c) => (
          <GemmaComponentCard key={c.id} component={c} niveau={0} />
        ))}
      </div>
    </section>
  );
}
