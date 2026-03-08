"use client";

import Link from "next/link";
import { useRecenteAanbestedingen } from "@/hooks/use-aanbestedingen";
import { Spinner } from "@/components/ui/Spinner";
import type { Aanbesteding } from "@/types/aanbestedingen";

// ── Helpers ────────────────────────────────────────────────────────────────────

const statusLabel: Record<string, string> = {
  aankondiging: "Aankondiging",
  gunning: "Gegund",
  rectificatie: "Rectificatie",
  vooraankondiging: "Vooraankondiging",
  ef25: "Vrijwillig gegund",
  onbekend: "Onbekend",
};

const statusKleur: Record<string, string> = {
  aankondiging: "bg-blue-100 text-blue-800",
  gunning: "bg-green-100 text-green-800",
  rectificatie: "bg-amber-100 text-amber-800",
  vooraankondiging: "bg-purple-100 text-purple-800",
  ef25: "bg-teal-100 text-teal-800",
  onbekend: "bg-gray-100 text-gray-600",
};

const typeLabel: Record<string, string> = {
  europees: "Europees",
  nationaal: "Nationaal",
  onbekend: "",
};

function formatBedrag(waarde?: number): string | null {
  if (!waarde) return null;
  if (waarde >= 1_000_000) {
    return `€ ${(waarde / 1_000_000).toFixed(1).replace(".", ",")} mln`;
  }
  return `€ ${Math.round(waarde).toLocaleString("nl-NL")}`;
}

function formatDatum(datum: string): string {
  try {
    return new Date(datum).toLocaleDateString("nl-NL", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  } catch {
    return datum;
  }
}

function dagenTotSluiting(sluitingsdatum?: string): number | null {
  if (!sluitingsdatum) return null;
  const nu = new Date();
  const sluiting = new Date(sluitingsdatum);
  const diff = Math.ceil((sluiting.getTime() - nu.getTime()) / (1000 * 60 * 60 * 24));
  return diff;
}

// ── Subcomponent: één rij ──────────────────────────────────────────────────────

function AanbestedingenRij({ aanbesteding }: { aanbesteding: Aanbesteding }) {
  const dagen = dagenTotSluiting(aanbesteding.sluitingsdatum);
  const bedrag = formatBedrag(aanbesteding.waarde_geschat);

  return (
    <li className="flex flex-col gap-1 py-4 sm:flex-row sm:items-start sm:justify-between">
      <div className="flex-1 min-w-0">
        {/* Naam als link naar TenderNed */}
        <a
          href={aanbesteding.url_tenderned}
          target="_blank"
          rel="noopener noreferrer"
          className="block font-medium text-gray-900 hover:text-primary-600 hover:underline truncate"
          title={aanbesteding.naam}
        >
          {aanbesteding.naam.length > 80
            ? `${aanbesteding.naam.slice(0, 77)}…`
            : aanbesteding.naam}
        </a>

        {/* Meta-rij */}
        <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-500">
          <span className="font-medium text-gray-700">
            {aanbesteding.aanbestedende_dienst}
          </span>
          <span>·</span>
          <span>{formatDatum(aanbesteding.publicatiedatum)}</span>
          {bedrag && (
            <>
              <span>·</span>
              <span className="text-gray-700">{bedrag}</span>
            </>
          )}
          {aanbesteding.gemma_component_namen.length > 0 && (
            <>
              <span>·</span>
              <span className="italic text-primary-600">
                GEMMA: {aanbesteding.gemma_component_namen.slice(0, 2).join(", ")}
              </span>
            </>
          )}
        </div>
      </div>

      {/* Badges rechts */}
      <div className="mt-2 flex flex-shrink-0 items-center gap-2 sm:mt-0 sm:ml-4">
        {/* Status badge */}
        <span
          className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
            statusKleur[aanbesteding.status] ?? statusKleur.onbekend
          }`}
        >
          {statusLabel[aanbesteding.status] ?? aanbesteding.status}
        </span>

        {/* Type badge (alleen Europees tonen) */}
        {aanbesteding.type === "europees" && (
          <span className="inline-flex items-center rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700">
            EU
          </span>
        )}

        {/* Sluiting */}
        {dagen !== null && dagen >= 0 && aanbesteding.status === "aankondiging" && (
          <span
            className={`text-xs ${
              dagen <= 7
                ? "font-semibold text-red-600"
                : dagen <= 14
                ? "font-medium text-amber-600"
                : "text-gray-500"
            }`}
          >
            {dagen === 0 ? "Sluit vandaag" : `Sluit over ${dagen}d`}
          </span>
        )}
      </div>
    </li>
  );
}

// ── Hoofdcomponent: widget ─────────────────────────────────────────────────────

interface AanbestedingenWidgetProps {
  /** Aantal te tonen aanbestedingen (standaard 5) */
  limit?: number;
  /** Toon compacte versie zonder header (voor dashboard) */
  compact?: boolean;
}

export function AanbestedingenWidget({
  limit = 5,
  compact = false,
}: AanbestedingenWidgetProps) {
  const { data, isLoading, error } = useRecenteAanbestedingen(limit);
  const aanbestedingen = data?.results ?? [];

  if (error) return null; // Stil falen — widget is aanvullend

  return (
    <section
      aria-labelledby="aanbestedingen-heading"
      className={compact ? "" : "rounded-lg border border-gray-200 bg-white p-6 shadow-sm"}
    >
      {!compact && (
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2
              id="aanbestedingen-heading"
              className="text-lg font-semibold text-gray-900"
            >
              Recente ICT-aanbestedingen
            </h2>
            <p className="mt-0.5 text-sm text-gray-500">
              Actuele aanbestedingen van Nederlandse gemeenten via TenderNed
            </p>
          </div>
          <a
            href="https://www.tenderned.nl"
            target="_blank"
            rel="noopener noreferrer"
            className="flex-shrink-0 text-xs text-gray-400 hover:text-primary-500"
            aria-label="Bekijk alle aanbestedingen op TenderNed (opent in nieuw tabblad)"
          >
            TenderNed ↗
          </a>
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-8" aria-busy="true">
          <Spinner className="h-6 w-6" />
          <span className="sr-only">Aanbestedingen laden…</span>
        </div>
      ) : aanbestedingen.length === 0 ? (
        <p className="py-4 text-center text-sm text-gray-400">
          Geen recente aanbestedingen gevonden.
        </p>
      ) : (
        <ul
          role="list"
          className="divide-y divide-gray-100"
          aria-label="Recente ICT-aanbestedingen"
        >
          {aanbestedingen.map((aanbesteding) => (
            <AanbestedingenRij
              key={aanbesteding.id}
              aanbesteding={aanbesteding}
            />
          ))}
        </ul>
      )}

      {!compact && data && data.count > limit && (
        <div className="mt-4 border-t border-gray-100 pt-4">
          <a
            href="https://www.tenderned.nl/aankondigingen"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-primary-600 hover:text-primary-700 hover:underline"
          >
            Bekijk alle {data.count} aanbestedingen op TenderNed →
          </a>
        </div>
      )}
    </section>
  );
}

// ── Compacte variant voor dashboard-kolom ─────────────────────────────────────

interface AanbestedingenDashboardSectieProps {
  /** Filteren op gemeente (naam) */
  gemeente?: string;
  /** Filteren op aanbesteding (voor leveranciers: via gemma-component namen) */
  aanbestedingen?: Aanbesteding[];
  isLoading?: boolean;
  titel?: string;
}

export function AanbestedingenDashboardSectie({
  aanbestedingen = [],
  isLoading = false,
  titel = "Relevante aanbestedingen",
}: AanbestedingenDashboardSectieProps) {
  if (isLoading) {
    return (
      <div className="flex justify-center py-4">
        <Spinner className="h-5 w-5" />
      </div>
    );
  }

  if (aanbestedingen.length === 0) {
    return (
      <p className="text-sm text-gray-400">
        Geen relevante aanbestedingen gevonden.
      </p>
    );
  }

  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-700 mb-2">{titel}</h3>
      <ul role="list" className="divide-y divide-gray-100 text-sm">
        {aanbestedingen.slice(0, 5).map((a) => (
          <li key={a.id} className="py-2">
            <a
              href={a.url_tenderned}
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-primary-600 hover:underline line-clamp-2"
            >
              {a.naam}
            </a>
            <div className="mt-0.5 text-xs text-gray-500">
              {a.aanbestedende_dienst} · {formatDatum(a.publicatiedatum)}
              {formatBedrag(a.waarde_geschat) && (
                <> · {formatBedrag(a.waarde_geschat)}</>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
