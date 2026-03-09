"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";

interface ConceptPakket {
  id: string;
  naam: string;
  versie: string;
  leverancier: { naam: string };
  status: string;
}

export default function BeheerPakkettenPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [foutBerichten, setFoutBerichten] = useState<Record<string, string>>({});

  const { data: concepten, isLoading } = useQuery({
    queryKey: ["admin-concept-pakketten"],
    queryFn: () =>
      api
        .get<{ results: ConceptPakket[] }>("/api/v1/pakketten/?status=concept")
        .then((r) => r.results),
    enabled: user?.rol === "functioneel_beheerder",
  });

  const fiateerMutatie = useMutation({
    mutationFn: (id: string) =>
      api.post(`/api/v1/pakketten/${id}/fiatteren/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-concept-pakketten"] });
    },
    onError: (err, id) => {
      const bericht =
        err instanceof ApiError
          ? err.getDetail("Fiattering mislukt.")
          : "Er is een fout opgetreden.";
      setFoutBerichten((prev) => ({ ...prev, [id]: bericht }));
    },
  });

  if (user?.rol !== "functioneel_beheerder") {
    return (
      <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
        U heeft geen toegang tot deze pagina.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Pakketbeheer</h1>
        <p className="mt-1 text-sm text-gray-600">
          Fiatteer nieuwe pakketregistraties zodat ze zichtbaar worden in de
          catalogus.
        </p>
      </div>

      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold">Wachtend op fiattering</h2>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : !concepten || concepten.length === 0 ? (
            <p className="py-4 text-center text-sm text-gray-500">
              Geen pakketten wachtend op fiattering.
            </p>
          ) : (
            <ul className="divide-y divide-gray-100">
              {concepten.map((pakket) => (
                <li
                  key={pakket.id}
                  className="flex items-center justify-between py-4"
                >
                  <div>
                    <p className="font-medium text-gray-900">
                      {pakket.naam}
                      {pakket.versie && (
                        <span className="ml-1 text-sm text-gray-500">
                          v{pakket.versie}
                        </span>
                      )}
                    </p>
                    <div className="mt-1 flex gap-2">
                      <Badge variant="info">
                        {pakket.leverancier?.naam ?? "—"}
                      </Badge>
                      <Badge variant="warning">Concept</Badge>
                    </div>
                    {foutBerichten[pakket.id] && (
                      <p className="mt-1 text-xs text-red-600">
                        {foutBerichten[pakket.id]}
                      </p>
                    )}
                  </div>
                  <Button
                    size="sm"
                    onClick={() => fiateerMutatie.mutate(pakket.id)}
                    disabled={fiateerMutatie.isPending}
                  >
                    Fiatteren
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
