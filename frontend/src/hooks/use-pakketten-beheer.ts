"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import type { GemmaComponent, Pakket, PakketInput, PaginatedResponse } from "@/types";

/**
 * Haalt de eigen pakketten van de ingelogde leverancier op.
 * Filtert op basis van user.organisatie zodat alleen de eigen pakketten
 * van de leverancier zichtbaar zijn.
 */
export function useEigenPakketten() {
  const { user } = useAuth();
  return useQuery({
    queryKey: ["eigen-pakketten", user?.organisatie],
    queryFn: () =>
      api.get<PaginatedResponse<Pakket>>("/api/v1/pakketten/", {
        params: user?.organisatie ? { leverancier: user.organisatie } : {},
      }),
    enabled: !!user?.organisatie,
  });
}

/**
 * Haalt één enkel pakket op voor het bewerkformulier.
 */
export function usePakket(id: string) {
  return useQuery({
    queryKey: ["pakket", id],
    queryFn: () => api.get<Pakket>(`/api/v1/pakketten/${id}/`),
    enabled: !!id,
  });
}

/**
 * Maakt een nieuw pakket aan (concept-status).
 * De leverancier wordt automatisch ingesteld vanuit user.organisatie.
 */
export function useAanmaakPakket() {
  const queryClient = useQueryClient();
  const { user } = useAuth();

  return useMutation({
    mutationFn: (data: PakketInput) =>
      api.post<Pakket>("/api/v1/pakketten/", {
        ...data,
        // Zorg dat leverancier altijd de eigen organisatie is
        leverancier: user?.organisatie ?? data.leverancier,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["eigen-pakketten"] });
    },
  });
}

/**
 * Werkt een bestaand pakket bij.
 */
export function useBijwerkPakket(id: string) {
  const queryClient = useQueryClient();
  const { user } = useAuth();

  return useMutation({
    mutationFn: (data: PakketInput) =>
      api.put<Pakket>(`/api/v1/pakketten/${id}/`, {
        ...data,
        leverancier: user?.organisatie ?? data.leverancier,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["eigen-pakketten"] });
      queryClient.invalidateQueries({ queryKey: ["pakket", id] });
    },
  });
}

/**
 * Haalt alle GEMMA-componenten op (publiek toegankelijk).
 * De endpoint heeft pagination_class=None zodat alle componenten in één call
 * worden teruggegeven als een gewone lijst (geen {count, results} wrapper).
 */
export function useGemmaComponenten() {
  return useQuery({
    queryKey: ["gemma-componenten"],
    queryFn: () => api.get<GemmaComponent[]>("/api/v1/gemma/componenten/"),
    staleTime: 10 * 60 * 1000, // 10 minuten — verandert zelden
  });
}

/**
 * Stelt de GEMMA-componentkoppelingen in voor een pakket.
 * Vervangt de volledige bestaande set.
 *
 * PUT /api/v1/pakketten/{id}/gemma-componenten/
 * Body: { gemma_component_ids: string[] }
 */
export function useStelPakketGemmaIn(pakketId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (gemma_component_ids: string[]) =>
      api.put<{ gemma_component_ids: string[]; gemma_componenten: GemmaComponent[] }>(
        `/api/v1/pakketten/${pakketId}/gemma-componenten/`,
        { gemma_component_ids }
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pakket", pakketId] });
      queryClient.invalidateQueries({ queryKey: ["eigen-pakketten"] });
    },
  });
}
