"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import type { Standaard, PaginatedResponse } from "@/types";

const typeVariant: Record<string, "danger" | "warning" | "default"> = {
  verplicht: "danger",
  aanbevolen: "warning",
  optioneel: "default",
};

const typeLabels: Record<string, string> = {
  verplicht: "Verplicht (pas toe of leg uit)",
  aanbevolen: "Aanbevolen",
  optioneel: "Optioneel",
};

export default function StandaardenPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["standaarden"],
    queryFn: () => api.get<PaginatedResponse<Standaard>>("/api/v1/standaarden/"),
  });

  const standaarden = data?.results || [];

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Standaarden</h1>
        <p className="mt-2 text-gray-600">
          Overzicht van standaarden uit het Forum Standaardisatie.
        </p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner className="h-8 w-8" />
        </div>
      ) : standaarden.length === 0 ? (
        <div className="rounded-md bg-gray-50 p-12 text-center text-gray-500">
          Geen standaarden beschikbaar.
        </div>
      ) : (
        <div className="space-y-3">
          {standaarden.map((s) => (
            <Card key={s.id}>
              <CardContent className="flex items-start justify-between gap-4 py-4">
                <div>
                  <h3 className="font-semibold text-gray-900">{s.naam}</h3>
                  {s.versie && (
                    <span className="text-sm text-gray-500">Versie {s.versie}</span>
                  )}
                  {s.beschrijving && (
                    <p className="mt-1 text-sm text-gray-600">{s.beschrijving}</p>
                  )}
                  {s.forum_standaardisatie_url && (
                    <a
                      href={s.forum_standaardisatie_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-1 inline-block text-xs text-primary-500 hover:underline"
                    >
                      Forum Standaardisatie &rarr;
                    </a>
                  )}
                </div>
                <Badge variant={typeVariant[s.type] || "default"}>
                  {typeLabels[s.type] || s.type}
                </Badge>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
