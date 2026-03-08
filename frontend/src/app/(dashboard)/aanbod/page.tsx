"use client";

import Link from "next/link";
import { useEigenPakketten } from "@/hooks/use-pakketten-beheer";
import { useAanbestedingen } from "@/hooks/use-aanbestedingen";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { AanbestedingenDashboardSectie } from "@/components/aanbestedingen/AanbestedingenWidget";
import type { Pakket } from "@/types";

// ── Labels en kleuren ──────────────────────────────────────────────────────────

const statusVariant: Record<string, "success" | "warning" | "default" | "danger"> = {
  actief: "success",
  concept: "warning",
  verouderd: "default",
  ingetrokken: "danger",
};

const statusLabel: Record<string, string> = {
  actief: "Actief",
  concept: "Concept",
  verouderd: "Verouderd",
  ingetrokken: "Ingetrokken",
};

const licentieLabel: Record<string, string> = {
  commercieel: "Commercieel",
  open_source: "Open source",
  saas: "SaaS",
  anders: "Anders",
};

// ── Component ──────────────────────────────────────────────────────────────────

export default function AanbodPage() {
  const { data, isLoading, error } = useEigenPakketten();
  const { data: aanbestedingenData, isLoading: aanbestedingenLoading } = useAanbestedingen({
    limit: 5,
    ordering: "-publicatiedatum",
  });

  const pakketten: Pakket[] = data?.results ?? [];
  const aanbestedingen = aanbestedingenData?.results ?? [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Pakketaanbod beheren</h1>
          <p className="mt-1 text-sm text-gray-600">
            Registreer en beheer de softwarepakketten van uw organisatie.
          </p>
        </div>
        <Link href="/aanbod/nieuw">
          <Button>Nieuw pakket</Button>
        </Link>
      </div>

      {/* Concept-status uitleg */}
      <div className="rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
        <strong>Concept-status:</strong> Nieuwe pakketten krijgen automatisch de status{" "}
        <span className="font-medium">Concept</span> en zijn pas zichtbaar in de publieke catalogus
        nadat een VNG Realisatie-beheerder ze heeft goedgekeurd.
      </div>

      {/* Inhoud */}
      {isLoading ? (
        <div className="flex justify-center py-16">
          <Spinner className="h-8 w-8" />
        </div>
      ) : error ? (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
          Er is een fout opgetreden bij het laden van uw pakketten. Controleer uw toegangsrechten.
        </div>
      ) : pakketten.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center">
            <p className="text-gray-500">U heeft nog geen pakketten geregistreerd.</p>
            <Link href="/aanbod/nieuw">
              <Button className="mt-4" variant="outline">
                Eerste pakket aanmaken
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                  Naam / Versie
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                  Licentie
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                  Gemeenten
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wide text-gray-500">
                  Acties
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {pakketten.map((pakket) => (
                <PakketRij key={pakket.id} pakket={pakket} />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Teller */}
      {!isLoading && pakketten.length > 0 && (
        <p className="text-sm text-gray-500">
          {pakketten.length} pakket{pakketten.length !== 1 ? "ten" : ""} gevonden
        </p>
      )}

      {/* TenderNed aanbestedingen — relevant voor leveranciers */}
      <div className="mt-8 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              Relevante aanbestedingen
            </h2>
            <p className="mt-0.5 text-sm text-gray-500">
              Recente ICT-aanbestedingen van Nederlandse gemeenten via TenderNed
            </p>
          </div>
          <a
            href="https://www.tenderned.nl"
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-gray-400 hover:text-primary-500"
          >
            TenderNed ↗
          </a>
        </div>
        <AanbestedingenDashboardSectie
          aanbestedingen={aanbestedingen}
          isLoading={aanbestedingenLoading}
          titel=""
        />
      </div>
    </div>
  );
}

// ── Tabelrij per pakket ────────────────────────────────────────────────────────

function PakketRij({ pakket }: { pakket: Pakket }) {
  return (
    <tr className="hover:bg-gray-50">
      {/* Naam + versie */}
      <td className="px-6 py-4">
        <div className="font-medium text-gray-900">{pakket.naam}</div>
        {pakket.versie && (
          <div className="text-xs text-gray-500">versie {pakket.versie}</div>
        )}
        {pakket.website_url && (
          <a
            href={pakket.website_url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-0.5 block text-xs text-primary-600 hover:underline"
          >
            {pakket.website_url}
          </a>
        )}
      </td>

      {/* Licentievorm */}
      <td className="px-6 py-4 text-sm text-gray-700">
        {licentieLabel[pakket.licentievorm] ?? pakket.licentievorm}
        {pakket.open_source_licentie && (
          <span className="ml-1 text-xs text-gray-400">({pakket.open_source_licentie})</span>
        )}
      </td>

      {/* Status */}
      <td className="px-6 py-4">
        <Badge variant={statusVariant[pakket.status] ?? "default"}>
          {statusLabel[pakket.status] ?? pakket.status}
        </Badge>
      </td>

      {/* Aantal gebruikende gemeenten */}
      <td className="px-6 py-4 text-sm text-gray-700">
        {pakket.aantal_gebruikers ?? 0}
      </td>

      {/* Acties */}
      <td className="px-6 py-4 text-right">
        <div className="flex justify-end gap-2">
          <Link href={`/pakketten/${pakket.id}`}>
            <Button size="sm" variant="ghost">
              Bekijk
            </Button>
          </Link>
          <Link href={`/aanbod/${pakket.id}/bewerken`}>
            <Button size="sm" variant="outline">
              Bewerken
            </Button>
          </Link>
        </div>
      </td>
    </tr>
  );
}
