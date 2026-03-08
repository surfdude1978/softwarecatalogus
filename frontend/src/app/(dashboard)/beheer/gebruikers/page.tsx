"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";

interface WachtendGebruiker {
  id: string;
  naam: string;
  email: string;
  rol: string;
  rol_display: string;
  organisatie: string | null;
  organisatie_naam: string | null;
  status: string;
  aangemaakt_op: string;
}

export default function BeheerGebruikersPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [foutBerichten, setFoutBerichten] = useState<Record<string, string>>({});

  const { data: wachtenden, isLoading } = useQuery({
    queryKey: ["admin-wachtende-gebruikers"],
    queryFn: () =>
      api.get<WachtendGebruiker[]>("/api/v1/admin/gebruikers/wachtend/"),
    enabled: user?.rol === "functioneel_beheerder",
  });

  const fiateerMutatie = useMutation({
    mutationFn: (id: string) =>
      api.post(`/api/v1/admin/gebruikers/${id}/fiatteren/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-wachtende-gebruikers"] });
    },
    onError: (err, id) => {
      const bericht =
        err instanceof ApiError
          ? err.getDetail("Fiattering mislukt.")
          : "Er is een fout opgetreden.";
      setFoutBerichten((prev) => ({ ...prev, [id]: bericht }));
    },
  });

  const afwijsMutatie = useMutation({
    mutationFn: (id: string) =>
      api.post(`/api/v1/admin/gebruikers/${id}/afwijzen/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-wachtende-gebruikers"] });
    },
    onError: (err, id) => {
      const bericht =
        err instanceof ApiError
          ? err.getDetail("Afwijzing mislukt.")
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

  const isBusy = fiateerMutatie.isPending || afwijsMutatie.isPending;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Gebruikersbeheer</h1>
        <p className="mt-1 text-sm text-gray-600">
          Beheer gebruikers en fiatteer nieuwe registraties.
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
          ) : !wachtenden || wachtenden.length === 0 ? (
            <p className="py-4 text-center text-sm text-gray-500">
              Geen gebruikers wachtend op fiattering.
            </p>
          ) : (
            <ul className="divide-y divide-gray-100">
              {wachtenden.map((gebruiker) => (
                <li key={gebruiker.id} className="py-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0 flex-1">
                      <p className="truncate font-medium text-gray-900">
                        {gebruiker.naam}
                      </p>
                      <p className="mt-0.5 text-sm text-gray-500">
                        {gebruiker.email}
                      </p>
                      <div className="mt-1.5 flex flex-wrap gap-2">
                        {gebruiker.organisatie_naam && (
                          <Badge variant="info">{gebruiker.organisatie_naam}</Badge>
                        )}
                        <Badge variant="default">{gebruiker.rol_display}</Badge>
                        <Badge variant="warning">Wacht op fiattering</Badge>
                      </div>
                      {foutBerichten[gebruiker.id] && (
                        <p className="mt-1 text-xs text-red-600">
                          {foutBerichten[gebruiker.id]}
                        </p>
                      )}
                    </div>
                    <div className="flex shrink-0 gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => afwijsMutatie.mutate(gebruiker.id)}
                        disabled={isBusy}
                      >
                        Afwijzen
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => fiateerMutatie.mutate(gebruiker.id)}
                        disabled={isBusy}
                      >
                        Fiatteren
                      </Button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
