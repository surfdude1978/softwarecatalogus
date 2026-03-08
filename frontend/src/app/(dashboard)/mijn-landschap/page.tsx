"use client";

import { useState } from "react";
import Link from "next/link";
import {
  useMijnPakketOverzicht,
  useVoegPakketToe,
  useVerwijderPakketGebruik,
} from "@/hooks/use-pakketoverzicht";
import { useGemeenteAanbestedingen } from "@/hooks/use-aanbestedingen";
import { useAuth } from "@/hooks/use-auth";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { AanbestedingenDashboardSectie } from "@/components/aanbestedingen/AanbestedingenWidget";
import { ExportKnoppen } from "@/components/export/ExportKnoppen";

const statusVariant: Record<string, "success" | "warning" | "default"> = {
  in_gebruik: "success",
  gepland: "warning",
  gestopt: "default",
};

const statusLabels: Record<string, string> = {
  in_gebruik: "In gebruik",
  gepland: "Gepland",
  gestopt: "Gestopt",
};

export default function MijnLandschapPage() {
  const { data, isLoading, error } = useMijnPakketOverzicht();
  const verwijderMutatie = useVerwijderPakketGebruik();
  const [verwijderConfirm, setVerwijderConfirm] = useState<string | null>(null);
  const [verwijderFout, setVerwijderFout] = useState<string | null>(null);
  const { user } = useAuth();

  // Strip "gemeente " prefix (hoofdletterongevoelig) voor betere TenderNed-match
  const gemeenteNaam = (user?.organisatie_naam ?? "")
    .replace(/^gemeente\s+/i, "")
    .trim();

  const { data: aanbestedingenData, isLoading: aanbestedingenLoading } =
    useGemeenteAanbestedingen(gemeenteNaam, 5);

  const pakketgebruik = data?.results || [];
  const aanbestedingen = aanbestedingenData?.results ?? [];

  const handleVerwijder = async (id: string) => {
    setVerwijderFout(null);
    try {
      await verwijderMutatie.mutateAsync(id);
    } catch {
      setVerwijderFout(
        "Verwijderen mislukt. Het pakket bestaat mogelijk niet meer — de lijst is bijgewerkt."
      );
    } finally {
      setVerwijderConfirm(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Mijn pakketlandschap</h1>
          <p className="mt-1 text-sm text-gray-600">
            Beheer de softwarepakketten van uw organisatie.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Link href="/mijn-landschap/architectuurkaart">
            <Button variant="outline" size="sm">
              🗺 Architectuurkaart
            </Button>
          </Link>
          <ExportKnoppen compact formaten={["xlsx", "csv", "ameff"]} />
          <Link href="/pakketten">
            <Button>Pakket toevoegen</Button>
          </Link>
        </div>
      </div>

      {verwijderFout && (
        <div className="flex items-center justify-between rounded-md bg-red-50 p-3 text-sm text-red-700">
          <span>{verwijderFout}</span>
          <button
            onClick={() => setVerwijderFout(null)}
            className="ml-4 text-red-500 hover:text-red-700"
            aria-label="Sluit foutmelding"
          >
            ✕
          </button>
        </div>
      )}

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner className="h-8 w-8" />
        </div>
      ) : error ? (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
          Er is een fout opgetreden bij het laden van uw pakketlandschap.
        </div>
      ) : pakketgebruik.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-500">
              U heeft nog geen pakketten geregistreerd.
            </p>
            <Link href="/pakketten">
              <Button className="mt-4" variant="outline">
                Bekijk de catalogus
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {pakketgebruik.map((pg: any) => (
            <Card key={pg.id}>
              <CardContent className="flex items-center justify-between py-4">
                <div className="flex items-center gap-4">
                  <div>
                    <Link
                      href={`/pakketten/${pg.pakket}`}
                      className="font-medium text-gray-900 hover:text-primary-500"
                    >
                      {pg.pakket_naam}
                    </Link>
                    {pg.start_datum && (
                      <p className="text-xs text-gray-500">
                        Sinds {new Date(pg.start_datum).toLocaleDateString("nl-NL")}
                      </p>
                    )}
                    {pg.notitie && (
                      <p className="mt-1 text-xs text-gray-500">{pg.notitie}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant={statusVariant[pg.status] || "default"}>
                    {statusLabels[pg.status] || pg.status}
                  </Badge>
                  {verwijderConfirm === pg.id ? (
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="danger"
                        onClick={() => handleVerwijder(pg.id)}
                        disabled={verwijderMutatie.isPending}
                      >
                        Bevestig
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setVerwijderConfirm(null)}
                      >
                        Annuleer
                      </Button>
                    </div>
                  ) : (
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setVerwijderConfirm(pg.id)}
                    >
                      Verwijder
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* TenderNed aanbestedingen — gefilterd op gemeente van gebruiker */}
      <div className="mt-4 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              ICT-aanbestedingen
              {gemeenteNaam && (
                <span className="ml-2 text-base font-normal text-gray-500">
                  — {user?.organisatie_naam ?? gemeenteNaam}
                </span>
              )}
            </h2>
            <p className="mt-0.5 text-sm text-gray-500">
              {gemeenteNaam
                ? `Actuele aanbestedingen van ${user?.organisatie_naam ?? gemeenteNaam} via TenderNed`
                : "Actuele ICT-aanbestedingen van Nederlandse gemeenten via TenderNed"}
            </p>
          </div>
          <a
            href={`https://www.tenderned.nl/aankondigingen${gemeenteNaam ? `?query=${encodeURIComponent(gemeenteNaam)}` : ""}`}
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
