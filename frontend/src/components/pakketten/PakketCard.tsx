import Link from "next/link";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent } from "@/components/ui/Card";

interface PakketCardProps {
  pakket: {
    id: string;
    naam: string;
    versie?: string;
    status: string;
    beschrijving: string;
    leverancier?: { naam: string } | null;
    leverancier_naam?: string;
    licentievorm: string;
    aantal_gebruikers: number;
  };
}

const licentieLabels: Record<string, string> = {
  commercieel: "Commercieel",
  open_source: "Open source",
  saas: "SaaS",
  anders: "Anders",
};

const statusVariant: Record<string, "success" | "warning" | "danger" | "default"> = {
  actief: "success",
  concept: "warning",
  verouderd: "danger",
  ingetrokken: "danger",
};

export function PakketCard({ pakket }: PakketCardProps) {
  const leverancierNaam = pakket.leverancier?.naam || pakket.leverancier_naam || "Onbekend";

  return (
    <Link href={`/pakketten/${pakket.id}`}>
      <Card className="h-full transition-shadow hover:shadow-md">
        <CardContent className="space-y-3">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold text-gray-900">
              {pakket.naam}
              {pakket.versie && (
                <span className="ml-1 text-sm font-normal text-gray-500">
                  v{pakket.versie}
                </span>
              )}
            </h3>
            <Badge variant={statusVariant[pakket.status] || "default"}>
              {pakket.status}
            </Badge>
          </div>
          <p className="line-clamp-2 text-sm text-gray-600">
            {pakket.beschrijving || "Geen beschrijving beschikbaar."}
          </p>
          <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500">
            <span>{leverancierNaam}</span>
            <span>{licentieLabels[pakket.licentievorm] || pakket.licentievorm}</span>
            <span>{pakket.aantal_gebruikers} gemeenten</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
