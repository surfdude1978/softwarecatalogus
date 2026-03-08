"use client";

import { useState } from "react";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";

const typeOpties = [
  { value: "gemeente", label: "Gemeente" },
  { value: "samenwerkingsverband", label: "Samenwerkingsverband" },
  { value: "leverancier", label: "Leverancier" },
  { value: "overig", label: "Overig" },
];

export default function OrganisatieRegistreerPage() {
  const [stap, setStap] = useState<"organisatie" | "gebruiker" | "succes">(
    "organisatie"
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [organisatieId, setOrganisatieId] = useState<string | null>(null);

  const [orgForm, setOrgForm] = useState({
    naam: "",
    type: "gemeente",
    website: "",
    oin: "",
  });

  const [userForm, setUserForm] = useState({
    naam: "",
    email: "",
    telefoon: "",
    password: "",
    password_confirm: "",
  });

  const updateOrg = (veld: string, waarde: string) =>
    setOrgForm((p) => ({ ...p, [veld]: waarde }));

  const updateUser = (veld: string, waarde: string) =>
    setUserForm((p) => ({ ...p, [veld]: waarde }));

  // ── Stap 1: Organisatie aanmaken ─────────────────────────────────────────

  const handleOrgSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      const data = await api.post<{ id: string }>("/api/v1/organisaties/", {
        naam: orgForm.naam,
        type: orgForm.type,
        website: orgForm.website || undefined,
        oin: orgForm.oin || undefined,
      });
      setOrganisatieId(data.id);
      setStap("gebruiker");
    } catch (err) {
      if (err instanceof ApiError) {
        const fieldErrors = err.getFieldErrors();
        const msgs = Object.values(fieldErrors).flat().join(" ");
        setError(msgs || err.getDetail("Organisatie aanmaken mislukt."));
      } else {
        setError("Er is een fout opgetreden.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // ── Stap 2: Eerste gebruiker aanmaken ────────────────────────────────────

  const handleUserSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (userForm.password !== userForm.password_confirm) {
      setError("Wachtwoorden komen niet overeen.");
      return;
    }
    if (userForm.password.length < 10) {
      setError("Wachtwoord moet minimaal 10 tekens bevatten.");
      return;
    }

    setIsLoading(true);
    try {
      await api.post("/api/v1/auth/registreer/", {
        naam: userForm.naam,
        email: userForm.email,
        telefoon: userForm.telefoon || undefined,
        organisatie: organisatieId,
        password: userForm.password,
        password_confirm: userForm.password_confirm,
      });
      setStap("succes");
    } catch (err) {
      if (err instanceof ApiError) {
        const fieldErrors = err.getFieldErrors();
        const msgs = Object.values(fieldErrors).flat().join(" ");
        setError(msgs || err.getDetail("Registratie mislukt."));
      } else {
        setError("Er is een fout opgetreden.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // ── Succes ────────────────────────────────────────────────────────────────

  if (stap === "succes") {
    return (
      <div className="flex min-h-[60vh] items-center justify-center px-4">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <h1 className="text-2xl font-bold text-gray-900">
              Registratie ingediend
            </h1>
            <p className="mt-4 text-gray-600">
              Uw organisatie en account zijn aangemaakt met de status{" "}
              <strong>concept</strong>. Een functioneel beheerder van VNG
              Realisatie zal uw aanvraag beoordelen. U ontvangt een e-mail
              zodra uw account is geactiveerd.
            </p>
            <Link href="/login">
              <Button className="mt-6">Naar inloggen</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex min-h-[60vh] items-center justify-center px-4 py-8">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <div className="flex items-center gap-2">
            <span
              className={`flex h-7 w-7 items-center justify-center rounded-full text-sm font-semibold ${
                stap === "organisatie"
                  ? "bg-primary-600 text-white"
                  : "bg-green-500 text-white"
              }`}
            >
              1
            </span>
            <span className="text-sm font-medium text-gray-700">
              Organisatiegegevens
            </span>
            <span className="mx-2 text-gray-300">→</span>
            <span
              className={`flex h-7 w-7 items-center justify-center rounded-full text-sm font-semibold ${
                stap === "gebruiker"
                  ? "bg-primary-600 text-white"
                  : "bg-gray-200 text-gray-500"
              }`}
            >
              2
            </span>
            <span className="text-sm font-medium text-gray-700">
              Accountgegevens
            </span>
          </div>
        </CardHeader>
        <CardContent className="p-8">
          {error && (
            <div
              className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700"
              role="alert"
            >
              {error}
            </div>
          )}

          {stap === "organisatie" && (
            <>
              <h1 className="text-xl font-bold text-gray-900">
                Nieuwe organisatie registreren
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Vul de gegevens van uw organisatie in. Na beoordeling door VNG
                Realisatie wordt uw organisatie geactiveerd.
              </p>
              <form onSubmit={handleOrgSubmit} className="mt-6 space-y-4">
                <Input
                  id="org-naam"
                  label="Organisatienaam *"
                  value={orgForm.naam}
                  onChange={(e) => updateOrg("naam", e.target.value)}
                  required
                  placeholder="Bijv. Gemeente Voorbeeldstad"
                />
                <Select
                  id="org-type"
                  label="Type organisatie *"
                  options={typeOpties}
                  value={orgForm.type}
                  onChange={(e) => updateOrg("type", e.target.value)}
                />
                <Input
                  id="org-oin"
                  label="OIN (optioneel)"
                  value={orgForm.oin}
                  onChange={(e) => updateOrg("oin", e.target.value)}
                  placeholder="Organisatie Identificatienummer"
                />
                <Input
                  id="org-website"
                  label="Website (optioneel)"
                  type="url"
                  value={orgForm.website}
                  onChange={(e) => updateOrg("website", e.target.value)}
                  placeholder="https://www.uw-organisatie.nl"
                />
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? "Bezig..." : "Volgende →"}
                </Button>
                <p className="text-center text-sm text-gray-500">
                  Sluit u aan bij een bestaande organisatie?{" "}
                  <Link
                    href="/registreer"
                    className="text-primary-500 hover:underline"
                  >
                    Terug naar registreren
                  </Link>
                </p>
              </form>
            </>
          )}

          {stap === "gebruiker" && (
            <>
              <h1 className="text-xl font-bold text-gray-900">
                Accountgegevens
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Maak het eerste account aan voor <strong>{orgForm.naam}</strong>.
              </p>
              <form onSubmit={handleUserSubmit} className="mt-6 space-y-4">
                <Input
                  id="user-naam"
                  label="Volledige naam *"
                  value={userForm.naam}
                  onChange={(e) => updateUser("naam", e.target.value)}
                  required
                />
                <Input
                  id="user-email"
                  label="E-mailadres *"
                  type="email"
                  value={userForm.email}
                  onChange={(e) => updateUser("email", e.target.value)}
                  required
                />
                <Input
                  id="user-telefoon"
                  label="Telefoonnummer (optioneel)"
                  type="tel"
                  value={userForm.telefoon}
                  onChange={(e) => updateUser("telefoon", e.target.value)}
                />
                <Input
                  id="user-password"
                  label="Wachtwoord (min. 10 tekens) *"
                  type="password"
                  value={userForm.password}
                  onChange={(e) => updateUser("password", e.target.value)}
                  required
                  minLength={10}
                />
                <Input
                  id="user-password-confirm"
                  label="Wachtwoord bevestigen *"
                  type="password"
                  value={userForm.password_confirm}
                  onChange={(e) => updateUser("password_confirm", e.target.value)}
                  required
                />
                <div className="flex gap-3">
                  <Button
                    type="button"
                    variant="outline"
                    className="flex-1"
                    onClick={() => setStap("organisatie")}
                  >
                    ← Terug
                  </Button>
                  <Button
                    type="submit"
                    className="flex-1"
                    disabled={isLoading}
                  >
                    {isLoading ? "Bezig..." : "Registratie indienen"}
                  </Button>
                </div>
              </form>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
