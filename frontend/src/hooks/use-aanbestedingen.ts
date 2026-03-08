"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Aanbesteding, AanbestedingenResponse } from "@/types/aanbestedingen";

const BASE = "/api/v1/aanbestedingen/";

/** Ophalen van recente ICT-aanbestedingen (homepage widget, geen context-filter) */
export function useRecenteAanbestedingen(limit: number = 5) {
  return useQuery<AanbestedingenResponse>({
    queryKey: ["aanbestedingen", "recent", limit],
    queryFn: () =>
      api.get<AanbestedingenResponse>(`${BASE}?limit=${limit}&ordering=-publicatiedatum`),
    staleTime: 1000 * 60 * 30, // 30 minuten cache
  });
}

/**
 * Aanbestedingen voor een specifieke gemeente (mijn-landschap context).
 *
 * Filtert op `aanbestedende_dienst__icontains=gemeenteNaam`.
 * Geef de naam zonder "gemeente "-prefix door (bijv. "Amsterdam" i.p.v. "Gemeente Amsterdam").
 */
export function useGemeenteAanbestedingen(gemeenteNaam: string, limit: number = 5) {
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

/**
 * Aanbestedingen relevant voor een leverancier (aanbod-context).
 *
 * De backend haalt de GEMMA-componenten op van alle pakketten van deze leverancier
 * en filtert aanbestedingen die aan die componenten gekoppeld zijn.
 * Als de leverancier nog geen GEMMA-koppelingen heeft, worden recente aanbestedingen getoond.
 *
 * @param organisatieId - UUID van de leverancier-organisatie
 */
export function useLeverancierAanbestedingen(
  organisatieId: string,
  limit: number = 5
) {
  return useQuery<AanbestedingenResponse>({
    queryKey: ["aanbestedingen", "leverancier", organisatieId, limit],
    queryFn: () =>
      api.get<AanbestedingenResponse>(
        `${BASE}?leverancier=${encodeURIComponent(organisatieId)}&limit=${limit}&ordering=-publicatiedatum`
      ),
    enabled: !!organisatieId,
    staleTime: 1000 * 60 * 30,
  });
}

/**
 * Aanbestedingen relevant voor een specifiek pakket (pakket-detail context).
 *
 * De backend haalt de GEMMA-componenten van het pakket op en filtert aanbestedingen
 * die aan dezelfde GEMMA-componenten gekoppeld zijn. Bij geen GEMMA-koppeling
 * wordt gezocht op pakketnaam.
 *
 * @param pakketId - UUID van het pakket
 */
export function usePakketAanbestedingen(pakketId: string, limit: number = 5) {
  return useQuery<AanbestedingenResponse>({
    queryKey: ["aanbestedingen", "pakket", pakketId, limit],
    queryFn: () =>
      api.get<AanbestedingenResponse>(
        `${BASE}?pakket=${encodeURIComponent(pakketId)}&limit=${limit}&ordering=-publicatiedatum`
      ),
    enabled: !!pakketId,
    staleTime: 1000 * 60 * 30,
  });
}

/** Generiek zoeken in aanbestedingen */
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
