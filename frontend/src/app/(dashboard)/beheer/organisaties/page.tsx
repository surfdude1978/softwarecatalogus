"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";

interface ConceptOrg {
  id: string;
  naam: string;
  type: string;
  type_display: string;
  status: string;
  website: string;
}

export default function BeheerOrganisatiesPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const { data: concepten, isLoading } = useQuery({
    queryKey: ["admin-concept-organisaties"],
    queryFn: () => api.get<ConceptOrg[]>("/api/v1/admin/organisaties/concept/"),
    enabled: user?.rol === "functioneel_beheerder",
  });

  const fiateerMutatie = useMutation({
    mutationFn: (id: string) =>
      api.post(`/api/v1/admin/organisaties/${id}/fiatteren/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-concept-organisaties"] });
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
        <h1 className="text-2xl font-bold text-gray-900">Organisatiebeheer</h1>
        <p className="mt-1 text-sm text-gray-600">
          Beheer organisaties en fiatteer nieuwe registraties.
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
              Geen organisaties wachtend op fiattering.
            </p>
          ) : (
            <ul className="divide-y divide-gray-100">
              {concepten.map((org) => (
                <li key={org.id} className="flex items-center justify-between py-4">
                  <div>
                    <p className="font-medium text-gray-900">{org.naam}</p>
                    <div className="mt-1 flex gap-2">
                      <Badge variant="info">{org.type_display}</Badge>
                      <Badge variant="warning">Concept</Badge>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    onClick={() => fiateerMutatie.mutate(org.id)}
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
