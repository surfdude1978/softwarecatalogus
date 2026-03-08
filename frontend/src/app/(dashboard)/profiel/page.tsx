"use client";

import { useAuth } from "@/hooks/use-auth";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

export default function ProfielPage() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Mijn profiel</h1>

      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold">Accountgegevens</h2>
        </CardHeader>
        <CardContent>
          <dl className="space-y-4">
            <ProfileRow label="Naam" value={user.naam} />
            <ProfileRow label="E-mailadres" value={user.email} />
            <ProfileRow
              label="Organisatie"
              value={user.organisatie_naam || "Niet gekoppeld"}
            />
            <ProfileRow label="Rol" value={user.rol_display} />
            <div className="flex items-center justify-between">
              <dt className="text-sm text-gray-500">2FA (TOTP)</dt>
              <dd>
                <Badge variant={user.totp_enabled ? "success" : "warning"}>
                  {user.totp_enabled ? "Ingeschakeld" : "Uitgeschakeld"}
                </Badge>
              </dd>
            </div>
          </dl>
        </CardContent>
      </Card>
    </div>
  );
}

function ProfileRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <dt className="text-sm text-gray-500">{label}</dt>
      <dd className="text-sm font-medium text-gray-900">{value}</dd>
    </div>
  );
}
