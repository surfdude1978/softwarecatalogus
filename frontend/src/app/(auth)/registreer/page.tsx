"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardContent } from "@/components/ui/Card";

export default function RegistreerPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const [form, setForm] = useState({
    email: "",
    naam: "",
    telefoon: "",
    password: "",
    password_confirm: "",
  });

  const updateField = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (form.password !== form.password_confirm) {
      setError("Wachtwoorden komen niet overeen.");
      return;
    }

    if (form.password.length < 10) {
      setError("Wachtwoord moet minimaal 10 tekens bevatten.");
      return;
    }

    setIsLoading(true);
    try {
      await api.post("/api/v1/auth/registreer/", form);
      setSuccess(true);
    } catch (err) {
      if (err instanceof ApiError) {
        try {
          const body = JSON.parse(err.body);
          const messages = Object.values(body).flat().join(" ");
          setError(messages || "Registratie mislukt.");
        } catch {
          setError("Registratie mislukt.");
        }
      } else {
        setError("Er is een fout opgetreden.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center px-4">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <h1 className="text-2xl font-bold text-gray-900">Registratie succesvol</h1>
            <p className="mt-4 text-gray-600">
              Uw account is aangemaakt en wacht op goedkeuring door de beheerder van uw organisatie.
              U ontvangt een e-mail zodra uw account is geactiveerd.
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
      <Card className="w-full max-w-md">
        <CardContent className="p-8">
          <h1 className="text-2xl font-bold text-gray-900">Registreren</h1>
          <p className="mt-2 text-sm text-gray-600">
            Maak een account aan voor de Softwarecatalogus.
          </p>

          {error && (
            <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700" role="alert">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <Input
              id="naam"
              label="Volledige naam"
              value={form.naam}
              onChange={(e) => updateField("naam", e.target.value)}
              required
            />
            <Input
              id="email"
              label="E-mailadres"
              type="email"
              value={form.email}
              onChange={(e) => updateField("email", e.target.value)}
              required
            />
            <Input
              id="telefoon"
              label="Telefoonnummer (optioneel)"
              type="tel"
              value={form.telefoon}
              onChange={(e) => updateField("telefoon", e.target.value)}
            />
            <Input
              id="password"
              label="Wachtwoord (min. 10 tekens)"
              type="password"
              value={form.password}
              onChange={(e) => updateField("password", e.target.value)}
              required
              minLength={10}
            />
            <Input
              id="password_confirm"
              label="Wachtwoord bevestigen"
              type="password"
              value={form.password_confirm}
              onChange={(e) => updateField("password_confirm", e.target.value)}
              required
            />
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Bezig..." : "Registreren"}
            </Button>
            <p className="text-center text-sm text-gray-500">
              Heeft u al een account?{" "}
              <Link href="/login" className="text-primary-500 hover:underline">
                Inloggen
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
