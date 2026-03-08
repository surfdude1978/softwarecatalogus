"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export interface KaartPakket {
  id: string;
  naam: string;
  leverancier_naam: string;
  status_gebruik: "in_gebruik" | "gepland" | "gestopt" | null;
  licentievorm: string;
}

export interface KaartComponent {
  id: string;
  naam: string;
  archimate_id: string;
  type: "applicatiecomponent" | "applicatieservice" | "applicatiefunctie" | "anders";
  type_display: string;
  beschrijving: string;
  gemma_online_url: string;
  kinderen: KaartComponent[];
  pakketten: KaartPakket[];
}

export interface GemmaKaartData {
  componenten: KaartComponent[];
}

export function useGemmaKaart() {
  return useQuery<GemmaKaartData>({
    queryKey: ["gemma-kaart"],
    queryFn: () => api.get<GemmaKaartData>("/api/v1/gemma/kaart/"),
    staleTime: 5 * 60 * 1000, // 5 minuten
  });
}
