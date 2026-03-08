"use client";

import Link from "next/link";
import { useGemmaKaart } from "@/hooks/use-gemma";
import { GemmaKaart } from "@/components/architectuur/GemmaKaart";
import { Spinner } from "@/components/ui/Spinner";
import { Button } from "@/components/ui/Button";

export default function ArchitectuurkaartPage() {
  const { data, isLoading, error, refetch } = useGemmaKaart();

  return (
    <div className="space-y-6">
      {/* Paginaheader */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <nav aria-label="Broodkruimel" className="mb-1 flex items-center gap-1 text-xs text-gray-500">
            <Link href="/mijn-landschap" className="hover:text-primary-500">
              Mijn pakketlandschap
            </Link>
            <span aria-hidden="true">›</span>
            <span className="text-gray-700" aria-current="page">
              Architectuurkaart
            </span>
          </nav>
          <h1 className="text-2xl font-bold text-gray-900">GEMMA Architectuurkaart</h1>
          <p className="mt-1 text-sm text-gray-600">
            Visueel overzicht van uw pakketlandschap gekoppeld aan de GEMMA
            referentiearchitectuur.
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <Link href="/mijn-landschap">
            <Button variant="outline" size="sm">
              ← Terug naar overzicht
            </Button>
          </Link>
          <Link href="/beheer/gemma">
            <Button variant="outline" size="sm">
              GEMMA beheer
            </Button>
          </Link>
        </div>
      </div>

      {/* Uitleg */}
      <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">
        <p>
          De kaart toont de GEMMA-componenten van de referentiearchitectuur. Per
          component ziet u welke pakketten uit uw landschap hieraan zijn
          gekoppeld, inclusief de gebruiksstatus.
        </p>
      </div>

      {/* Inhoud */}
      {isLoading ? (
        <div className="flex justify-center py-16" role="status" aria-label="Architectuurkaart laden">
          <Spinner className="h-8 w-8" />
        </div>
      ) : error ? (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert">
          <p className="font-medium">Fout bij laden van de architectuurkaart</p>
          <p className="mt-1 text-red-600">
            Controleer of de backend bereikbaar is en probeer het opnieuw.
          </p>
          <Button
            variant="outline"
            size="sm"
            className="mt-3"
            onClick={() => refetch()}
          >
            Opnieuw proberen
          </Button>
        </div>
      ) : (
        <GemmaKaart
          componenten={data?.componenten ?? []}
          metLegenda
        />
      )}
    </div>
  );
}
