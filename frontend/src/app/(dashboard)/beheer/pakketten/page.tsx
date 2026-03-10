"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { Input } from "@/components/ui/Input";
import { Pagination } from "@/components/ui/Pagination";

interface ConceptPakket {
  id: string;
  naam: string;
  versie: string;
  leverancier: { id: string; naam: string };
  status: string;
  beschrijving: string;
  licentievorm: string;
  licentievorm_display: string;
  geregistreerd_door_naam: string | null;
  geregistreerd_door_email: string | null;
  aangemaakt_op: string;
}

interface PaginatedResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: ConceptPakket[];
}

function relatieveDatum(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const dagen = Math.floor(diff / 86400000);
  if (dagen === 0) return "vandaag";
  if (dagen === 1) return "gisteren";
  if (dagen < 7) return `${dagen} dagen geleden`;
  if (dagen < 30) return `${Math.floor(dagen / 7)} weken geleden`;
  return `${Math.floor(dagen / 30)} maanden geleden`;
}

const PAGE_SIZE = 10;

export default function BeheerPakkettenPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [zoekterm, setZoekterm] = useState("");
  const [pagina, setPagina] = useState(1);
  const [afwijzenId, setAfwijzenId] = useState<string | null>(null);
  const [afwijzenNaam, setAfwijzenNaam] = useState("");
  const [reden, setReden] = useState("");
  const [redenFout, setRedenFout] = useState("");
  const [foutBerichten, setFoutBerichten] = useState<Record<string, string>>({});

  const { data, isLoading } = useQuery({
    queryKey: ["admin-concept-pakketten", zoekterm, pagina],
    queryFn: () => {
      const params = new URLSearchParams({
        status: "concept",
        page: String(pagina),
        page_size: String(PAGE_SIZE),
      });
      if (zoekterm) params.set("search", zoekterm);
      return api.get<PaginatedResponse>(`/api/v1/pakketten/?${params}`);
    },
    enabled: user?.rol === "functioneel_beheerder",
  });

  const fiateerMutatie = useMutation({
    mutationFn: (id: string) => api.post(`/api/v1/pakketten/${id}/fiatteren/`),
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

  const afwijzenMutatie = useMutation({
    mutationFn: ({ id, reden }: { id: string; reden: string }) =>
      api.post(`/api/v1/pakketten/${id}/afwijzen/`, { reden }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-concept-pakketten"] });
      sluitAfwijzenModal();
    },
    onError: (err) => {
      const bericht =
        err instanceof ApiError
          ? err.getDetail("Afwijzing mislukt.")
          : "Er is een fout opgetreden.";
      setRedenFout(bericht);
    },
  });

  function openAfwijzenModal(id: string, naam: string) {
    setAfwijzenId(id);
    setAfwijzenNaam(naam);
    setReden("");
    setRedenFout("");
  }

  function sluitAfwijzenModal() {
    setAfwijzenId(null);
    setAfwijzenNaam("");
    setReden("");
    setRedenFout("");
  }

  function bevestigAfwijzen() {
    if (!afwijzenId) return;
    if (!reden.trim()) {
      setRedenFout("Vul een reden in voor de afwijzing.");
      return;
    }
    afwijzenMutatie.mutate({ id: afwijzenId, reden });
  }

  if (user?.rol !== "functioneel_beheerder") {
    return (
      <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
        U heeft geen toegang tot deze pagina.
      </div>
    );
  }

  const concepten = data?.results ?? [];
  const totaal = data?.count ?? 0;
  const totalePaginas = Math.ceil(totaal / PAGE_SIZE);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Pakketbeheer</h1>
        <p className="mt-1 text-sm text-gray-600">
          Fiatteer of wijs nieuwe pakketregistraties af zodat ze zichtbaar
          worden in de catalogus.
        </p>
      </div>

      {/* Statistieken */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-sm text-gray-500">Wachtend op beoordeling</p>
          <p className="mt-1 text-3xl font-bold text-gray-900">
            {isLoading ? "—" : totaal}
          </p>
        </div>
      </div>

      {/* Zoekbalk */}
      <div className="max-w-md">
        <Input
          placeholder="Zoek op naam of leverancier…"
          value={zoekterm}
          onChange={(e) => {
            setZoekterm(e.target.value);
            setPagina(1);
          }}
        />
      </div>

      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold">
            Wachtend op fiattering
            {totaal > 0 && (
              <span className="ml-2 rounded-full bg-yellow-100 px-2 py-0.5 text-sm font-medium text-yellow-800">
                {totaal}
              </span>
            )}
          </h2>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : concepten.length === 0 ? (
            <p className="py-4 text-center text-sm text-gray-500">
              {zoekterm
                ? "Geen resultaten voor deze zoekopdracht."
                : "Geen pakketten wachtend op fiattering."}
            </p>
          ) : (
            <ul className="divide-y divide-gray-100">
              {concepten.map((pakket) => (
                <li key={pakket.id} className="py-5">
                  <div className="flex items-start justify-between gap-4">
                    {/* Info kolom */}
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <Link
                          href={`/pakketten/${pakket.id}`}
                          className="font-medium text-gray-900 hover:text-blue-700"
                        >
                          {pakket.naam}
                        </Link>
                        {pakket.versie && (
                          <span className="text-sm text-gray-500">
                            v{pakket.versie}
                          </span>
                        )}
                        <Badge variant="warning">Concept</Badge>
                      </div>

                      <div className="mt-1.5 flex flex-wrap gap-2">
                        <Badge variant="info">
                          {pakket.leverancier?.naam ?? "—"}
                        </Badge>
                        {pakket.licentievorm_display && (
                          <Badge variant="default">
                            {pakket.licentievorm_display}
                          </Badge>
                        )}
                      </div>

                      {pakket.beschrijving && (
                        <p className="mt-2 line-clamp-2 text-sm text-gray-600">
                          {pakket.beschrijving}
                        </p>
                      )}

                      <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500">
                        {pakket.geregistreerd_door_naam && (
                          <span>
                            Ingediend door{" "}
                            <span className="font-medium text-gray-700">
                              {pakket.geregistreerd_door_naam}
                            </span>
                            {pakket.geregistreerd_door_email && (
                              <> ({pakket.geregistreerd_door_email})</>
                            )}
                          </span>
                        )}
                        {pakket.aangemaakt_op && (
                          <span>{relatieveDatum(pakket.aangemaakt_op)}</span>
                        )}
                      </div>

                      {foutBerichten[pakket.id] && (
                        <p className="mt-1 text-xs text-red-600">
                          {foutBerichten[pakket.id]}
                        </p>
                      )}
                    </div>

                    {/* Actie knoppen */}
                    <div className="flex shrink-0 gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          openAfwijzenModal(pakket.id, pakket.naam)
                        }
                        disabled={fiateerMutatie.isPending}
                      >
                        Afwijzen
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => fiateerMutatie.mutate(pakket.id)}
                        disabled={fiateerMutatie.isPending}
                      >
                        Fiatteren
                      </Button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}

          {totalePaginas > 1 && (
            <div className="mt-4 border-t border-gray-100 pt-4">
              <Pagination
                currentPage={pagina}
                totalPages={totalePaginas}
                onPageChange={setPagina}
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Afwijzen modal */}
      {afwijzenId && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
          onClick={sluitAfwijzenModal}
        >
          <div
            className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-semibold text-gray-900">
              Pakket afwijzen
            </h3>
            <p className="mt-1 text-sm text-gray-600">
              U staat op het punt{" "}
              <span className="font-medium">{afwijzenNaam}</span> af te wijzen.
              De indiener ontvangt een notificatie met uw reden.
            </p>

            <div className="mt-4">
              <label
                htmlFor="reden"
                className="block text-sm font-medium text-gray-700"
              >
                Reden van afwijzing <span className="text-red-500">*</span>
              </label>
              <textarea
                id="reden"
                rows={4}
                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="Geef een duidelijke toelichting…"
                value={reden}
                onChange={(e) => {
                  setReden(e.target.value);
                  setRedenFout("");
                }}
              />
              {redenFout && (
                <p className="mt-1 text-xs text-red-600">{redenFout}</p>
              )}
            </div>

            <div className="mt-5 flex justify-end gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={sluitAfwijzenModal}
                disabled={afwijzenMutatie.isPending}
              >
                Annuleren
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={bevestigAfwijzen}
                disabled={afwijzenMutatie.isPending}
              >
                {afwijzenMutatie.isPending ? "Bezig…" : "Afwijzen bevestigen"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
