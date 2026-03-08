"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardContent } from "@/components/ui/Card";

export default function LoginPage() {
  const router = useRouter();
  const { login, verifyTotp, isLoading, error, clearError } = useAuth();
  const [step, setStep] = useState<"credentials" | "totp">("credentials");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [totpCode, setTotpCode] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    try {
      const result = await login(email, password);
      if (result.totp_required) {
        setStep("totp");
      } else {
        router.push("/mijn-landschap");
      }
    } catch {
      // Error handled by store
    }
  };

  const handleTotp = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    try {
      await verifyTotp(totpCode);
      router.push("/mijn-landschap");
    } catch {
      // Error handled by store
    }
  };

  return (
    <div className="flex min-h-[60vh] items-center justify-center px-4">
      <Card className="w-full max-w-md">
        <CardContent className="p-8">
          <h1 className="text-2xl font-bold text-gray-900">Inloggen</h1>
          <p className="mt-2 text-sm text-gray-600">
            {step === "credentials"
              ? "Log in op de Softwarecatalogus."
              : "Voer de code in van uw authenticator app."}
          </p>

          {error && (
            <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700" role="alert">
              {error}
            </div>
          )}

          {step === "credentials" ? (
            <form onSubmit={handleLogin} className="mt-6 space-y-4">
              <Input
                id="email"
                label="E-mailadres"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
              <Input
                id="password"
                label="Wachtwoord"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Bezig..." : "Inloggen"}
              </Button>
              <div className="flex justify-between text-sm">
                <Link href="/registreer" className="text-primary-500 hover:underline">
                  Registreren
                </Link>
                <Link href="/wachtwoord-vergeten" className="text-gray-500 hover:underline">
                  Wachtwoord vergeten?
                </Link>
              </div>
            </form>
          ) : (
            <form onSubmit={handleTotp} className="mt-6 space-y-4">
              <Input
                id="totp-code"
                label="Verificatiecode"
                type="text"
                inputMode="numeric"
                pattern="[0-9]{6}"
                maxLength={6}
                value={totpCode}
                onChange={(e) => setTotpCode(e.target.value)}
                required
                autoComplete="one-time-code"
                placeholder="000000"
              />
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Bezig..." : "Verifieer"}
              </Button>
              <button
                type="button"
                onClick={() => setStep("credentials")}
                className="w-full text-sm text-gray-500 hover:underline"
              >
                Terug naar inloggen
              </button>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
