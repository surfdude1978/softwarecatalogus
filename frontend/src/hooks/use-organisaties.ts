"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Organisatie, PaginatedResponse } from "@/types";

interface OrganisatieFilters {
  page?: number;
  type?: string;
  search?: string;
  ordering?: string;
}

export function useOrganisaties(filters: OrganisatieFilters = {}) {
  const params: Record<string, string> = {};
  if (filters.page) params.page = String(filters.page);
  if (filters.type) params.type = filters.type;
  if (filters.search) params.search = filters.search;
  if (filters.ordering) params.ordering = filters.ordering;

  return useQuery({
    queryKey: ["organisaties", filters],
    queryFn: () => api.get<PaginatedResponse<Organisatie>>("/api/v1/organisaties/", { params }),
  });
}

export function useOrganisatie(id: string) {
  return useQuery({
    queryKey: ["organisatie", id],
    queryFn: () => api.get<Organisatie>(`/api/v1/organisaties/${id}/`),
    enabled: !!id,
  });
}
