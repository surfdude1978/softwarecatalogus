"use client";

import Link from "next/link";
import { usePakket } from "@/hooks/use-pakketten";
import { usePakketAanbestedingen } from "@/hooks/use-aanbestedingen";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { Button } from "@/components/ui/Button";
import { AanbestedingenDashboardSectie } from "@/components/aanbestedingen/AanbestedingenWidget";

const statusVariant: Record<string, "success" | "warning" | "danger" | "default"> = {
  actief: "success",
  concept: "warning",
  verouderd: "danger",
  ingetrokken: "danger",
};

const licentieLabels: Record<string, string> = {
  commercieel: "Commercieel",
  open_source: "Open source",
  saas: "SaaS",
  anders: "Anders",
};

export default function PakketDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const { id } = params;
  const { data: pakket, isLoading, error } = usePakket(id);
  const {
    data: aanbestedingenData,
    isLoading: aanbestedingenLoading,
  } = usePakketAanbestedingen(id);

  if (isLoading) {
    return (
      <div className="flex justify-center py-24">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  if (error || !pakket) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12">
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
          Pakket niet gevonden of er is een fout opgetreden.
        </div>
        <Link href="/pakketten" className="mt-4 inline-block text-sm text-primary-500 hover:underline">
          Terug naar pakketten
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <Link href="/pakketten" className="mb-6 inline-block text-sm text-primary-500 hover:underline">
        &larr; Terug naar pakketten
      </Link>

      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {pakket.naam}
              {pakket.versie && (
                <span className="ml-2 text-lg font-normal text-gray-500">
                  v{pakket.versie}
                </span>
              )}
            </h1>
            <p className="mt-1 text-gray-600">
              {pakket.leverancier?.naam || "Onbekende leverancier"}
            </p>
          </div>
          <Badge variant={statusVariant[pakket.status] || "default"} className="text-sm">
            {pakket.status}
          </Badge>
        </div>

        {/* Beschrijving */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold">Beschrijving</h2>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-line text-gray-700">
              {pakket.beschrijving || "Geen beschrijving beschikbaar."}
            </p>
          </CardContent>
        </Card>

        {/* Details */}
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold">Gegevens</h2>
            </CardHeader>
            <CardContent>
              <dl className="space-y-3">
                <DetailRow label="Licentievorm" value={licentieLabels[pakket.licentievorm] || pakket.licentievorm} />
                {pakket.open_source_licentie && (
                  <DetailRow label="Open source licentie" value={pakket.open_source_licentie} />
                )}
                {pakket.cloud_provider && (
                  <DetailRow label="Cloud provider" value={pakket.cloud_provider} />
                )}
                <DetailRow
                  label="Aantal gemeenten"
                  value={String(pakket.aantal_gebruikers || 0)}
                />
              </dl>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold">Links</h2>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {pakket.website_url && (
                  <a
                    href={pakket.website_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-sm text-primary-500 hover:underline"
                  >
                    Website &rarr;
                  </a>
                )}
                {pakket.documentatie_url && (
                  <a
                    href={pakket.documentatie_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-sm text-primary-500 hover:underline"
                  >
                    Documentatie &rarr;
                  </a>
                )}
                {!pakket.website_url && !pakket.documentatie_url && (
                  <p className="text-sm text-gray-500">Geen links beschikbaar.</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Standaarden */}
        {(pakket as any).standaarden?.length > 0 && (
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold">Ondersteunde standaarden</h2>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {(pakket as any).standaarden.map((s: any) => (
                  <Badge key={s.id} variant={s.type === "verplicht" ? "info" : "default"}>
                    {s.naam}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* GEMMA componenten */}
        {(pakket as any).gemma_componenten?.length > 0 && (
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold">GEMMA componenten</h2>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {(pakket as any).gemma_componenten.map((c: any) => (
                  <Badge key={c.id} variant="default">
                    {c.naam}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Relevante aanbestedingen — gefilterd op GEMMA-componenten van dit pakket */}
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Relevante aanbestedingen
              </h2>
              <p className="mt-0.5 text-sm text-gray-500">
                Actuele ICT-aanbestedingen gerelateerd aan dit pakket via TenderNed
              </p>
            </div>
            <a
              href={`https://www.tenderned.nl/aankondigingen?query=${encodeURIComponent(pakket.naam)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-gray-400 hover:text-primary-500"
            >
              TenderNed ↗
            </a>
          </div>
          <AanbestedingenDashboardSectie
            aanbestedingen={aanbestedingenData?.results ?? []}
            isLoading={aanbestedingenLoading}
            titel=""
          />
        </div>

        {/* Gebruikende organisaties */}
        {(pakket as any).gebruikende_organisaties?.length > 0 && (
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold">Gebruikt door</h2>
            </CardHeader>
            <CardContent>
              <ul className="divide-y divide-gray-100">
                {(pakket as any).gebruikende_organisaties.map((org: any) => (
                  <li key={org.id} className="py-2">
                    <Link
                      href={`/organisaties/${org.id}`}
                      className="text-sm text-primary-500 hover:underline"
                    >
                      {org.naam}
                    </Link>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between text-sm">
      <dt className="text-gray-500">{label}</dt>
      <dd className="font-medium text-gray-900">{value}</dd>
    </div>
  );
}
