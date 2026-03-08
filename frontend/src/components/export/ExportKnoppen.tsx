"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { AUTH_COOKIE_MODE } from "@/lib/api";

// ── Types ───────────────────────────────────────────────────────────────────

type ExportFormaat = "csv" | "xlsx" | "ameff";

interface ExportOptie {
  formaat: ExportFormaat;
  label: string;
  beschrijving: string;
  endpoint: string;
  contentType: string;
  bestandsextensie: string;
}

// ── Config ──────────────────────────────────────────────────────────────────

const EXPORT_OPTIES: ExportOptie[] = [
  {
    formaat: "xlsx",
    label: "Excel",
    beschrijving: "Download als Excel-spreadsheet (.xlsx)",
    endpoint: "/api/v1/export/pakketoverzicht.xlsx",
    contentType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    bestandsextensie: "xlsx",
  },
  {
    formaat: "csv",
    label: "CSV",
    beschrijving: "Download als kommagescheiden bestand (.csv)",
    endpoint: "/api/v1/export/pakketoverzicht.csv",
    contentType: "text/csv",
    bestandsextensie: "csv",
  },
  {
    formaat: "ameff",
    label: "AMEFF",
    beschrijving: "ArchiMate Exchange formaat voor Archi, BiZZdesign, Sparx EA",
    endpoint: "/api/v1/export/pakketoverzicht.ameff",
    contentType: "application/xml",
    bestandsextensie: "ameff",
  },
];

// ── Hook ────────────────────────────────────────────────────────────────────

function useExport() {
  const [bezig, setBezig] = useState<ExportFormaat | null>(null);
  const [fout, setFout] = useState<string | null>(null);

  const download = async (optie: ExportOptie) => {
    setBezig(optie.formaat);
    setFout(null);

    try {
      const fetchOpts: RequestInit = AUTH_COOKIE_MODE
        ? { credentials: "include" }
        : { headers: { Authorization: `Bearer ${localStorage.getItem("access_token") ?? ""}` } };

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}${optie.endpoint}`,
        fetchOpts
      );

      if (!response.ok) {
        const msg =
          response.status === 401
            ? "U bent niet ingelogd."
            : response.status === 400
            ? "Geen organisatie gekoppeld aan uw account."
            : `Download mislukt (${response.status}).`;
        throw new Error(msg);
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;

      // Bestandsnaam uit Content-Disposition header ophalen
      const disposition = response.headers.get("content-disposition") ?? "";
      const match = disposition.match(/filename="?([^";\n]+)"?/);
      a.download = match?.[1] ?? `pakketoverzicht.${optie.bestandsextensie}`;

      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setFout(err instanceof Error ? err.message : "Download mislukt.");
    } finally {
      setBezig(null);
    }
  };

  return { download, bezig, fout };
}

// ── Componenten ─────────────────────────────────────────────────────────────

interface ExportKnoppenProps {
  /** Compact weergave: alleen icoonknoppen zonder beschrijving */
  compact?: boolean;
  /** Welke formaten beschikbaar zijn (standaard: alle drie) */
  formaten?: ExportFormaat[];
}

/**
 * Export-knoppen voor pakketoverzicht (CSV, Excel, AMEFF).
 * Vereist ingelogde gebruiker met gekoppelde organisatie.
 */
export function ExportKnoppen({
  compact = false,
  formaten = ["xlsx", "csv", "ameff"],
}: ExportKnoppenProps) {
  const { download, bezig, fout } = useExport();

  const beschikbareOpties = EXPORT_OPTIES.filter((o) =>
    formaten.includes(o.formaat)
  );

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        {beschikbareOpties.map((optie) => (
          <button
            key={optie.formaat}
            onClick={() => download(optie)}
            disabled={bezig !== null}
            title={optie.beschrijving}
            className="inline-flex items-center gap-1 rounded border border-gray-200 bg-white px-2 py-1 text-xs font-medium text-gray-600 hover:border-primary-300 hover:text-primary-600 disabled:opacity-50"
          >
            {bezig === optie.formaat ? (
              <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-current border-t-transparent" />
            ) : (
              <DownloadIcon className="h-3 w-3" />
            )}
            {optie.label}
          </button>
        ))}
      </div>
    );
  }

  return (
    <div>
      <div className="flex flex-wrap gap-2">
        {beschikbareOpties.map((optie) => (
          <Button
            key={optie.formaat}
            variant="outline"
            size="sm"
            onClick={() => download(optie)}
            disabled={bezig !== null}
            className="gap-1.5"
          >
            {bezig === optie.formaat ? (
              <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
            ) : (
              <DownloadIcon className="h-4 w-4" />
            )}
            {optie.label}
          </Button>
        ))}
      </div>

      {fout && (
        <p className="mt-2 text-xs text-red-600" role="alert">
          {fout}
        </p>
      )}
    </div>
  );
}

// ── Icoon ───────────────────────────────────────────────────────────────────

function DownloadIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 20 20"
      fill="currentColor"
      className={className}
      aria-hidden="true"
    >
      <path d="M10.75 2.75a.75.75 0 0 0-1.5 0v8.614L6.295 8.235a.75.75 0 1 0-1.09 1.03l4.25 4.5a.75.75 0 0 0 1.09 0l4.25-4.5a.75.75 0 0 0-1.09-1.03l-2.955 3.129V2.75Z" />
      <path d="M3.5 12.75a.75.75 0 0 0-1.5 0v2.5A2.75 2.75 0 0 0 4.75 18h10.5A2.75 2.75 0 0 0 18 15.25v-2.5a.75.75 0 0 0-1.5 0v2.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-2.5Z" />
    </svg>
  );
}
