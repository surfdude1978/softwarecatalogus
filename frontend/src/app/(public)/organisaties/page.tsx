"use client";

import { useState } from "react";
import Link from "next/link";
import { useOrganisaties } from "@/hooks/use-organisaties";
import { Select } from "@/components/ui/Select";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { Pagination } from "@/components/ui/Pagination";

const PAGE_SIZE = 25;

const typeLabels: Record<string, string> = {
  gemeente: "Gemeente",
  samenwerkingsverband: "Samenwerkingsverband",
  leverancier: "Leverancier",
  overig: "Overig",
};

const typeBadgeVariant: Record<string, "info" | "success" | "warning" | "default"> = {
  gemeente: "info",
  leverancier: "success",
  samenwerkingsverband: "warning",
  overig: "default",
};

export default function OrganisatiesPage() {
  const [page, setPage] = useState(1);
  const [type, setType] = useState("");
  const [search, setSearch] = useState("");

  const { data, isLoading, error } = useOrganisaties({
    page,
    type: type || undefined,
    search: search || undefined,
    ordering: "naam",
  });

  const organisaties = data?.results || [];
  const totalPages = Math.ceil((data?.count || 0) / PAGE_SIZE);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Organisaties</h1>
        <p className="mt-2 text-gray-600">
          Bekijk gemeenten, leveranciers en samenwerkingsverbanden.
        </p>
      </div>

      <div className="mb-6 flex flex-wrap gap-4">
        <div className="w-64">
          <Input
            id="zoek-org"
            placeholder="Zoek op naam..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </div>
        <Select
          id="filter-type"
          placeholder="Alle typen"
          value={type}
          onChange={(e) => {
            setType(e.target.value);
            setPage(1);
          }}
          options={[
            { value: "gemeente", label: "Gemeenten" },
            { value: "leverancier", label: "Leveranciers" },
            { value: "samenwerkingsverband", label: "Samenwerkingsverbanden" },
          ]}
        />
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner className="h-8 w-8" />
        </div>
      ) : error ? (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
          Er is een fout opgetreden bij het laden van organisaties.
        </div>
      ) : organisaties.length === 0 ? (
        <div className="rounded-md bg-gray-50 p-12 text-center text-gray-500">
          Geen organisaties gevonden.
        </div>
      ) : (
        <>
          <p className="mb-4 text-sm text-gray-500">
            {data?.count || 0} organisatie{(data?.count || 0) !== 1 ? "s" : ""} gevonden
          </p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {organisaties.map((org) => (
              <Link key={org.id} href={`/organisaties/${org.id}`}>
                <Card className="h-full transition-shadow hover:shadow-md">
                  <CardContent>
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="font-semibold text-gray-900">{org.naam}</h3>
                      <Badge variant={typeBadgeVariant[org.type] || "default"}>
                        {typeLabels[org.type] || org.type}
                      </Badge>
                    </div>
                    {org.website && (
                      <p className="mt-2 truncate text-xs text-gray-500">{org.website}</p>
                    )}
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
          <div className="mt-6">
            <Pagination
              currentPage={page}
              totalPages={totalPages}
              onPageChange={setPage}
            />
          </div>
        </>
      )}
    </div>
  );
}
