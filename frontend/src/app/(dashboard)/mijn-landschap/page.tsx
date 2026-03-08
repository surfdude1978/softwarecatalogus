"use client";

import { useState } from "react";
import Link from "next/link";
import {
  useMijnPakketOverzicht,
  useVoegPakketToe,
  useVerwijderPakketGebruik,
} from "@/hooks/use-pakketoverzicht";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";

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

  const pakketgebruik = data?.results || [];

  const handleVerwijder = async (id: string) => {
    await verwijderMutatie.mutateAsync(id);
    setVerwijderConfirm(null);
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
        <Link href="/pakketten">
          <Button>Pakket toevoegen</Button>
        </Link>
      </div>

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
    </div>
  );
}
