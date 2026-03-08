"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import type { GemmaComponent, PaginatedResponse } from "@/types";

export default function BeheerGemmaPage() {
  const { user } = useAuth();
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["gemma-componenten"],
    queryFn: () =>
      api.get<PaginatedResponse<GemmaComponent>>("/api/v1/gemma/componenten/", {
        params: { page_size: "100" },
      }),
  });

  const handleUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const file = formData.get("bestand") as File;

    if (!file) {
      setUploadStatus("Selecteer een AMEFF-bestand.");
      return;
    }

    setUploadStatus("Bezig met importeren...");
    setUploadResult(null);

    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch("/api/v1/admin/gemma/importeer/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setUploadStatus("Import succesvol!");
        setUploadResult(result);
      } else {
        setUploadStatus(result.detail || "Import mislukt.");
      }
    } catch {
      setUploadStatus("Er is een fout opgetreden.");
    }
  };

  if (user?.rol !== "functioneel_beheerder") {
    return (
      <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
        U heeft geen toegang tot deze pagina.
      </div>
    );
  }

  const componenten = data?.results || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">GEMMA beheer</h1>
        <p className="mt-1 text-sm text-gray-600">
          Importeer GEMMA referentiecomponenten en beheer de architectuurkaart.
        </p>
      </div>

      {/* Import */}
      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold">AMEFF importeren</h2>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleUpload} className="space-y-4">
            <div>
              <label
                htmlFor="ameff-bestand"
                className="block text-sm font-medium text-gray-700"
              >
                AMEFF XML-bestand
              </label>
              <input
                id="ameff-bestand"
                name="bestand"
                type="file"
                accept=".xml,.ameff"
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:rounded-md file:border-0 file:bg-primary-50 file:px-4 file:py-2 file:text-sm file:font-medium file:text-primary-700 hover:file:bg-primary-100"
              />
            </div>
            <Button type="submit">Importeren</Button>
          </form>

          {uploadStatus && (
            <div
              className={`mt-4 rounded-md p-3 text-sm ${
                uploadStatus.includes("succesvol")
                  ? "bg-green-50 text-green-700"
                  : uploadStatus.includes("Bezig")
                    ? "bg-blue-50 text-blue-700"
                    : "bg-red-50 text-red-700"
              }`}
            >
              {uploadStatus}
            </div>
          )}

          {uploadResult?.statistieken && (
            <div className="mt-4 rounded-md bg-gray-50 p-4">
              <h3 className="text-sm font-medium text-gray-700">Resultaat:</h3>
              <dl className="mt-2 grid grid-cols-2 gap-2 text-sm">
                <dt className="text-gray-500">Elementen gevonden:</dt>
                <dd>{uploadResult.statistieken.elementen_gevonden}</dd>
                <dt className="text-gray-500">Aangemaakt:</dt>
                <dd className="text-green-700">{uploadResult.statistieken.aangemaakt}</dd>
                <dt className="text-gray-500">Bijgewerkt:</dt>
                <dd>{uploadResult.statistieken.bijgewerkt}</dd>
              </dl>
              {uploadResult.conflicten?.length > 0 && (
                <div className="mt-3">
                  <h4 className="text-sm font-medium text-yellow-700">
                    Conflicten ({uploadResult.conflicten.length}):
                  </h4>
                  <ul className="mt-1 text-xs text-yellow-600">
                    {uploadResult.conflicten.map((c: any, i: number) => (
                      <li key={i}>
                        {c.archimate_id}: &quot;{c.old_name}&quot; &rarr; &quot;{c.new_name}&quot;
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Componenten overzicht */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">
              GEMMA componenten ({componenten.length})
            </h2>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : componenten.length === 0 ? (
            <p className="py-4 text-center text-sm text-gray-500">
              Nog geen GEMMA componenten geimporteerd.
            </p>
          ) : (
            <div className="max-h-96 overflow-y-auto">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-white text-left text-gray-500">
                  <tr>
                    <th className="pb-2 font-medium">Naam</th>
                    <th className="pb-2 font-medium">Type</th>
                    <th className="pb-2 font-medium">ArchiMate ID</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {componenten.map((c) => (
                    <tr key={c.id}>
                      <td className="py-2 font-medium text-gray-900">{c.naam}</td>
                      <td className="py-2">
                        <Badge variant="default">{c.type}</Badge>
                      </td>
                      <td className="py-2 text-xs text-gray-500">
                        {c.archimate_id}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
