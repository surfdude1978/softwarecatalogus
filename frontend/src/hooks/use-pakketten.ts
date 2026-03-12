"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Pakket, PaginatedResponse } from "@/types";

interface PakketFilters {
  search?: string;
  page?: number;
  status?: string;
  licentievorm?: string;
  leverancier?: string;
  standaard?: string;
  gemma_component?: string;
  ordering?: string;
}

interface SearchResult {
  hits: Array<{
    id: string;
    naam: string;
    versie: string;
    status: string;
    beschrijving: string;
    leverancier_naam: string;
    licentievorm: string;
    aantal_gebruikers: number;
  }>;
  total: number;
  offset: number;
  limit: number;
}

export function usePakketten(filters: PakketFilters = {}) {
  const params: Record<string, string> = {};
  if (filters.page) params.page = String(filters.page);
  if (filters.status) params.status = filters.status;
  if (filters.licentievorm) params.licentievorm = filters.licentievorm;
  if (filters.leverancier) params.leverancier = filters.leverancier;
  if (filters.ordering) params.ordering = filters.ordering;
  if (filters.search) params.search = filters.search;

  return useQuery({
    queryKey: ["pakketten", filters],
    queryFn: () => api.get<PaginatedResponse<Pakket>>("/api/v1/pakketten/", { params }),
  });
}

export function usePakket(id: string) {
  return useQuery({
    queryKey: ["pakket", id],
    queryFn: () => api.get<Pakket>(`/api/v1/pakketten/${id}/`),
    enabled: !!id,
  });
}

// Map DRF-style ordering naar Meilisearch sort parameter
const ORDERING_TO_SORT: Record<string, string> = {
  "naam": "naam:asc",
  "-naam": "naam:desc",
  "-aantal_gebruikers": "populair",
  "-gewijzigd_op": "recent",
};

export function useZoekPakketten(query: string, filters: Omit<PakketFilters, "search" | "page"> & { offset?: number } = {}) {
  const params: Record<string, string> = { q: query };
  if (filters.licentievorm) params.licentievorm = filters.licentievorm;
  if (filters.leverancier) params.leverancier = filters.leverancier;
  if (filters.standaard) params.standaard = filters.standaard;
  if (filters.gemma_component) params.gemma_component = filters.gemma_component;
  if (filters.ordering) params.sort = ORDERING_TO_SORT[filters.ordering] || filters.ordering;
  if (filters.offset) params.offset = String(filters.offset);

  return useQuery({
    queryKey: ["zoek-pakketten", query, filters],
    queryFn: () => api.get<SearchResult>("/api/v1/zoek/", { params }),
    enabled: query.length >= 2,
  });
}
