"use client";
// v2
import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { usePakket, useBijwerkPakket } from "@/hooks/use-pakketten-beheer";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Spinner } from "@/components/ui/Spinner";
import { ApiError } from "@/lib/api";
import type { PakketInput } from "@/types";

// ── Opties ────────────────────────────────────────────────────────────────────

const licentieOpties = [
  { value: "commercieel", label: "Commercieel" },
  { value: "open_source", label: "Open source" },
  { value: "saas", label: "SaaS (cloud-hosted)" },
  { value: "anders", label: "Anders" },
];

const statusLabel: Record<string, string> = {
  actief: "Actief",
  concept: "Concept",
  verouderd: "Verouderd",
  ingetrokken: "Ingetrokken",
};

const statusVariant: Record<string, "success" | "warning" | "default" | "danger"> = {
  actief: "success",
  concept: "warning",
  verouderd: "default",
  ingetrokken: "danger",
};

// ── Component ──────────────────────────────────────────────────────────────────

export default function BewerkPakketPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { data: pakket, isLoading, error: laadFout } = usePakket(params.id);
  const bijwerk = useBijwerkPakket(params.id);

  const [form, setForm] = useState<PakketInput>({
    naam: "",
    versie: "",
    beschrijving: "",
    licentievorm: "commercieel",
    open_source_licentie: "",
    website_url: "",
    documentatie_url: "",
    cloud_provider: "",
  });

  const [fouten, setFouten] = useState<Partial<Record<keyof PakketInput, string>>>({});
  const [apiError, setApiError] = useState<string | null>(null);
  const [geinitialiseerd, setGeinitialiseerd] = useState(false);

  // Vul formulier zodra pakketdata binnenkomt
  useEffect(() => {
    if (pakket && !geinitialiseerd) {
      setForm({
        naam: pakket.naam,
        versie: pakket.versie ?? "",
        beschrijving: pakket.beschrijving ?? "",
        licentievorm: pakket.licentievorm,
        open_source_licentie: pakket.open_source_licentie ?? "",
        website_url: pakket.website_url ?? "",
        documentatie_url: pakket.documentatie_url ?? "",
        cloud_provider: pakket.cloud_provider ?? "",
      });
      setGeinitialiseerd(true);
    }
  }, [pakket, geinitialiseerd]);

  // ── Validatie ────────────────────────────────────────────────────────────────

  function valideer(): boolean {
    const nieuweFouten: typeof fouten = {};
    if (!form.naam.trim()) {
      nieuweFouten.naam = "Naam is verplicht.";
    }
    setFouten(nieuweFouten);
    return Object.keys(nieuweFouten).length === 0;
  }

  // ── Handlers ──────────────────────────────────────────────────────────────────

  function stelIn<K extends keyof PakketInput>(veld: K, waarde: PakketInput[K]) {
    setForm((prev) => ({ ...prev, [veld]: waarde }));
    if (fouten[veld]) {
      setFouten((prev) => ({ ...prev, [veld]: undefined }));
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setApiError(null);
    if (!valideer()) return;

    const payload: PakketInput = {
      naam: form.naam.trim(),
      licentievorm: form.licentievorm,
      ...(form.versie?.trim() && { versie: form.versie.trim() }),
      ...(form.beschrijving?.trim() && { beschrijving: form.beschrijving.trim() }),
      ...(form.licentievorm === "open_source" && form.open_source_licentie?.trim() && {
        open_source_licentie: form.open_source_licentie.trim(),
      }),
      ...(form.website_url?.trim() && { website_url: form.website_url.trim() }),
      ...(form.documentatie_url?.trim() && { documentatie_url: form.documentatie_url.trim() }),
      ...(form.cloud_provider?.trim() && { cloud_provider: form.cloud_provider.trim() }),
    };

    try {
      await bijwerk.mutateAsync(payload);
      router.push("/aanbod");
    } catch (err) {
      if (err instanceof ApiError) {
        try {
          const body = JSON.parse(err.body);
          const veldFouten: typeof fouten = {};
          for (const [veld, berichten] of Object.entries(body)) {
            if (Array.isArray(berichten)) {
              veldFouten[veld as keyof PakketInput] = berichten.join(" ");
            }
          }
          if (Object.keys(veldFouten).length > 0) {
            setFouten(veldFouten);
          } else {
            setApiError(body.detail ?? "Er is een fout opgetreden bij het opslaan.");
          }
        } catch {
          setApiError("Er is een onverwachte fout opgetreden.");
        }
      } else {
        setApiError("Er is een onverwachte fout opgetreden.");
      }
    }
  }

  // ── Laadstatus ────────────────────────────────────────────────────────────────

  if (isLoading) {
    return (
      <div className="flex justify-center py-16">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  if (laadFout || !pakket) {
    return (
      <div className="space-y-4">
        <Link href="/aanbod">
          <Button variant="ghost" size="sm">← Terug</Button>
        </Link>
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
          Pakket niet gevonden of u heeft geen toegang om dit pakket te bewerken.
        </div>
      </div>
    );
  }

  // ── Render ────────────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/aanbod">
          <Button variant="ghost" size="sm">← Terug</Button>
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">{pakket.naam} bewerken</h1>
            <Badge variant={statusVariant[pakket.status] ?? "default"}>
              {statusLabel[pakket.status] ?? pakket.status}
            </Badge>
          </div>
          <p className="mt-1 text-sm text-gray-600">
            Wijzigingen aan een actief pakket zijn direct zichtbaar in de catalogus.
          </p>
        </div>
      </div>

      {/* Formulier */}
      <form onSubmit={handleSubmit} noValidate>
        <div className="space-y-6">
          {/* Basisgegevens */}
          <Card>
            <CardHeader>
              <h2 className="text-base font-semibold text-gray-900">Basisgegevens</h2>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input
                id="naam"
                label="Naam *"
                placeholder="Bijv. Suite4Gemeenten"
                value={form.naam}
                onChange={(e) => stelIn("naam", e.target.value)}
                error={fouten.naam}
                required
              />

              <Input
                id="versie"
                label="Versie"
                placeholder="Bijv. 2024.1"
                value={form.versie ?? ""}
                onChange={(e) => stelIn("versie", e.target.value)}
              />

              <div className="space-y-1">
                <label htmlFor="beschrijving" className="block text-sm font-medium text-gray-700">
                  Beschrijving
                </label>
                <textarea
                  id="beschrijving"
                  rows={4}
                  placeholder="Korte omschrijving van het pakket en zijn functionaliteiten…"
                  value={form.beschrijving ?? ""}
                  onChange={(e) => stelIn("beschrijving", e.target.value)}
                  className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder:text-gray-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                />
              </div>
            </CardContent>
          </Card>

          {/* Licentie */}
          <Card>
            <CardHeader>
              <h2 className="text-base font-semibold text-gray-900">Licentie</h2>
            </CardHeader>
            <CardContent className="space-y-4">
              <Select
                id="licentievorm"
                label="Licentievorm *"
                options={licentieOpties}
                value={form.licentievorm}
                onChange={(e) =>
                  stelIn("licentievorm", e.target.value as PakketInput["licentievorm"])
                }
              />

              {form.licentievorm === "open_source" && (
                <Input
                  id="open_source_licentie"
                  label="Open source licentie"
                  placeholder="Bijv. EUPL-1.2, MIT, GPL-3.0"
                  value={form.open_source_licentie ?? ""}
                  onChange={(e) => stelIn("open_source_licentie", e.target.value)}
                />
              )}
            </CardContent>
          </Card>

          {/* Links */}
          <Card>
            <CardHeader>
              <h2 className="text-base font-semibold text-gray-900">Links en informatie</h2>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input
                id="website_url"
                label="Website URL"
                type="url"
                placeholder="https://www.voorbeeld.nl"
                value={form.website_url ?? ""}
                onChange={(e) => stelIn("website_url", e.target.value)}
                error={fouten.website_url}
              />

              <Input
                id="documentatie_url"
                label="Documentatie URL"
                type="url"
                placeholder="https://docs.voorbeeld.nl"
                value={form.documentatie_url ?? ""}
                onChange={(e) => stelIn("documentatie_url", e.target.value)}
                error={fouten.documentatie_url}
              />

              <Input
                id="cloud_provider"
                label="Cloud provider"
                placeholder="Bijv. Microsoft Azure, AWS, eigen hosting"
                value={form.cloud_provider ?? ""}
                onChange={(e) => stelIn("cloud_provider", e.target.value)}
              />
            </CardContent>
          </Card>

          {/* API-fout */}
          {apiError && (
            <div className="rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert">
              {apiError}
            </div>
          )}

          {/* Acties */}
          <div className="flex justify-end gap-3">
            <Link href="/aanbod">
              <Button type="button" variant="outline">
                Annuleren
              </Button>
            </Link>
            <Button type="submit" disabled={bijwerk.isPending}>
              {bijwerk.isPending ? "Opslaan…" : "Wijzigingen opslaan"}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}
