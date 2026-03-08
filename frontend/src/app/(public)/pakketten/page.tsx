"use client";

import { useState } from "react";
import { usePakketten, useZoekPakketten } from "@/hooks/use-pakketten";
import { PakketCard } from "@/components/pakketten/PakketCard";
import { PakketFilters } from "@/components/pakketten/PakketFilters";
import { ZoekBalk } from "@/components/pakketten/ZoekBalk";
import { Pagination } from "@/components/ui/Pagination";
import { Spinner } from "@/components/ui/Spinner";

const PAGE_SIZE = 25;

export default function PakkettenPage() {
  const [zoekterm, setZoekterm] = useState("");
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    licentievorm: "",
    status: "",
    ordering: "naam",
  });

  const isSearching = zoekterm.length >= 2;

  const browseQuery = usePakketten({
    page,
    ...filters,
    search: isSearching ? undefined : undefined,
  });

  const searchQuery = useZoekPakketten(zoekterm, {
    licentievorm: filters.licentievorm || undefined,
    ordering: filters.ordering || undefined,
    offset: (page - 1) * PAGE_SIZE,
  });

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const handleSearch = (query: string) => {
    setZoekterm(query);
    setPage(1);
  };

  const isLoading = isSearching ? searchQuery.isLoading : browseQuery.isLoading;
  const error = isSearching ? searchQuery.error : browseQuery.error;

  // Normalize results
  const pakketten = isSearching
    ? (searchQuery.data?.hits || [])
    : (browseQuery.data?.results || []);

  const totalCount = isSearching
    ? (searchQuery.data?.total || 0)
    : (browseQuery.data?.count || 0);

  const totalPages = Math.ceil(totalCount / PAGE_SIZE);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Pakketten</h1>
        <p className="mt-2 text-gray-600">
          Zoek en vergelijk softwarepakketten in de catalogus.
        </p>
      </div>

      <div className="space-y-6">
        <ZoekBalk onSearch={handleSearch} defaultValue={zoekterm} />
        <PakketFilters filters={filters} onChange={handleFilterChange} />

        {isLoading ? (
          <div className="flex justify-center py-12">
            <Spinner className="h-8 w-8" />
          </div>
        ) : error ? (
          <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
            Er is een fout opgetreden bij het laden van pakketten.
          </div>
        ) : pakketten.length === 0 ? (
          <div className="rounded-md bg-gray-50 p-12 text-center text-gray-500">
            Geen pakketten gevonden.
            {zoekterm && " Probeer een andere zoekterm."}
          </div>
        ) : (
          <>
            <p className="text-sm text-gray-500">
              {totalCount} pakket{totalCount !== 1 ? "ten" : ""} gevonden
            </p>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {pakketten.map((pakket: any) => (
                <PakketCard key={pakket.id} pakket={pakket} />
              ))}
            </div>
            <Pagination
              currentPage={page}
              totalPages={totalPages}
              onPageChange={setPage}
            />
          </>
        )}
      </div>
    </div>
  );
}
