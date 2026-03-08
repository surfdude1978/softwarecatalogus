"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { PakketGebruik, PaginatedResponse } from "@/types";

export function useMijnPakketOverzicht() {
  return useQuery({
    queryKey: ["mijn-pakketoverzicht"],
    queryFn: () =>
      api.get<PaginatedResponse<PakketGebruik>>(
        "/api/v1/mijn-organisatie/pakketoverzicht/"
      ),
  });
}

export function useGemeentePakketOverzicht(gemeenteId: string) {
  return useQuery({
    queryKey: ["gemeente-pakketoverzicht", gemeenteId],
    queryFn: () =>
      api.get<PakketGebruik[]>(
        `/api/v1/gemeenten/${gemeenteId}/pakketoverzicht/`
      ),
    enabled: !!gemeenteId,
  });
}

export function useVoegPakketToe() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      pakket: string;
      status?: string;
      start_datum?: string;
      notitie?: string;
    }) => api.post<PakketGebruik>("/api/v1/mijn-organisatie/pakketoverzicht/", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mijn-pakketoverzicht"] });
    },
  });
}

export function useVerwijderPakketGebruik() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) =>
      api.delete(`/api/v1/mijn-organisatie/pakketoverzicht/${id}/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mijn-pakketoverzicht"] });
    },
    onError: () => {
      // Ververs de lijst bij een fout (bijv. 404 door verouderde cache)
      queryClient.invalidateQueries({ queryKey: ["mijn-pakketoverzicht"] });
    },
  });
}
