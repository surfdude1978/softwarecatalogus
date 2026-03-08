/**
 * TypeScript types voor TenderNed aanbestedingen.
 */

export type AanbestedingenType = "europees" | "nationaal" | "onbekend";

export type AanbestedingenStatus =
  | "aankondiging"
  | "gunning"
  | "rectificatie"
  | "vooraankondiging"
  | "ef25"
  | "onbekend";

export interface Aanbesteding {
  id: string;
  publicatiecode: string;
  naam: string;
  aanbestedende_dienst: string;
  aanbestedende_dienst_naam: string;
  aanbestedende_dienst_stad: string;
  type: AanbestedingenType;
  status: AanbestedingenStatus;
  procedure?: string;
  publicatiedatum: string;   // ISO date string
  sluitingsdatum?: string;   // ISO date string
  primaire_cpv?: string;
  cpv_omschrijvingen: string[];
  waarde_geschat?: number;
  url_tenderned: string;
  omschrijving?: string;
  gemma_component_namen: string[];
}

export interface AanbestedingenResponse {
  count: number;
  next?: string;
  previous?: string;
  results: Aanbesteding[];
}
