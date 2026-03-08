"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Aanbesteding, AanbestedingenResponse } from "@/types/aanbestedingen";

const BASE = "/api/v1/aanbestedingen/";

/** Ophalen van recente ICT-aanbestedingen (homepage widget) */
export function useRecenteAanbestedingen(limit: number = 5) {
  return useQuery<AanbestedingenResponse>({
    queryKey: ["aanbestedingen", "recent", limit],
    queryFn: () =>
      api.get<AanbestedingenResponse>(`${BASE}?limit=${limit}&ordering=-publicatiedatum`),
    staleTime: 1000 * 60 * 30, // 30 minuten cache
  });
}

/** Aanbestedingen voor een specifieke gemeente (via naam) */
export function useGemeenteAanbestedingen(gemeenteNaam: string, limit: number = 10) {
  return useQuery<AanbestedingenResponse>({
    queryKey: ["aanbestedingen", "gemeente", gemeenteNaam, limit],
    queryFn: () =>
      api.get<AanbestedingenResponse>(
        `${BASE}?gemeente=${encodeURIComponent(gemeenteNaam)}&limit=${limit}&ordering=-publicatiedatum`
      ),
    enabled: !!gemeenteNaam,
    staleTime: 1000 * 60 * 30,
  });
}

/** Aanbestedingen relevant voor een leverancier (via GEMMA-componenten van hun pakketten) */
export function useLeverancierAanbestedingen(
  gemmaComponentNamen: string[],
  limit: number = 10
) {
  const params = gemmaComponentNamen
    .map((naam) => `search=${encodeURIComponent(naam)}`)
    .join("&");

  return useQuery<AanbestedingenResponse>({
    queryKey: ["aanbestedingen", "leverancier", gemmaComponentNamen, limit],
    queryFn: () =>
      api.get<AanbestedingenResponse>(
        `${BASE}?${params}&limit=${limit}&ordering=-publicatiedatum`
      ),
    enabled: gemmaComponentNamen.length > 0,
    staleTime: 1000 * 60 * 30,
  });
}

/** Zoeken in aanbestedingen */
export function useAanbestedingen(params: {
  search?: string;
  type?: string;
  status?: string;
  limit?: number;
  ordering?: string;
} = {}) {
  const searchParams = new URLSearchParams();
  if (params.search) searchParams.set("search", params.search);
  if (params.type) searchParams.set("type", params.type);
  if (params.status) searchParams.set("status", params.status);
  if (params.limit) searchParams.set("limit", String(params.limit));
  if (params.ordering) searchParams.set("ordering", params.ordering);

  const queryString = searchParams.toString();

  return useQuery<AanbestedingenResponse>({
    queryKey: ["aanbestedingen", params],
    queryFn: () =>
      api.get<AanbestedingenResponse>(`${BASE}${queryString ? `?${queryString}` : ""}`),
    staleTime: 1000 * 60 * 15,
  });
}
