import Link from "next/link";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";

const typeLabels: Record<string, string> = {
  gemeente: "Gemeente",
  samenwerkingsverband: "Samenwerkingsverband",
  leverancier: "Leverancier",
  overig: "Overig",
};

async function getOrganisatie(id: string) {
  // In server-side rendering, use Docker internal hostname
  const apiUrl = process.env.API_URL || "http://backend:8000";
  try {
    const res = await fetch(`${apiUrl}/api/v1/organisaties/${id}/`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch (error) {
    console.error("Error fetching organisatie:", error);
    return null;
  }
}

export default async function OrganisatieDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const { id } = params;
  const org = await getOrganisatie(id);

  if (!org) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12">
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
          Organisatie niet gevonden.
        </div>
        <Link href="/organisaties" className="mt-4 inline-block text-sm text-primary-500 hover:underline">
          Terug naar organisaties
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <Link href="/organisaties" className="mb-6 inline-block text-sm text-primary-500 hover:underline">
        &larr; Terug naar organisaties
      </Link>

      <div className="space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{org.naam}</h1>
            <p className="mt-1 text-gray-500">{typeLabels[org.type] || org.type}</p>
          </div>
          <Badge variant={org.status === "actief" ? "success" : "warning"}>
            {org.status}
          </Badge>
        </div>

        {org.beschrijving && (
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold">Over deze organisatie</h2>
            </CardHeader>
            <CardContent>
              <p className="whitespace-pre-line text-gray-700">{org.beschrijving}</p>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold">Gegevens</h2>
          </CardHeader>
          <CardContent>
            <dl className="space-y-3">
              {org.oin && (
                <div className="flex justify-between text-sm">
                  <dt className="text-gray-500">OIN</dt>
                  <dd className="font-medium text-gray-900">{org.oin}</dd>
                </div>
              )}
              {org.website && (
                <div className="flex justify-between text-sm">
                  <dt className="text-gray-500">Website</dt>
                  <dd>
                    <a
                      href={org.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary-500 hover:underline"
                    >
                      {org.website}
                    </a>
                  </dd>
                </div>
              )}
            </dl>
          </CardContent>
        </Card>

        {/* Contactpersonen */}
        {(org as any).contactpersonen?.length > 0 && (
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold">Contactpersonen</h2>
            </CardHeader>
            <CardContent>
              <ul className="divide-y divide-gray-100">
                {(org as any).contactpersonen.map((cp: any) => (
                  <li key={cp.id} className="py-3">
                    <p className="font-medium text-gray-900">{cp.naam}</p>
                    {cp.functie && <p className="text-sm text-gray-500">{cp.functie}</p>}
                    <p className="text-sm text-gray-600">{cp.email}</p>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
