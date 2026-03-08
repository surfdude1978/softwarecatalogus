/**
 * TypeScript types voor de Softwarecatalogus.
 * In een later stadium worden deze gegenereerd vanuit de OpenAPI spec.
 */

export interface Organisatie {
  id: string;
  naam: string;
  type: "gemeente" | "samenwerkingsverband" | "leverancier" | "overig";
  status: "concept" | "actief" | "inactief";
  oin: string;
  website: string;
  beschrijving: string;
}

export interface GemmaComponent {
  id: string;
  naam: string;
  archimate_id: string;
  type: "applicatiecomponent" | "applicatieservice" | "applicatiefunctie" | "anders";
  beschrijving: string;
  gemma_online_url: string;
}

export interface Pakket {
  id: string;
  naam: string;
  versie: string;
  status: "concept" | "actief" | "verouderd" | "ingetrokken";
  beschrijving: string;
  leverancier: Organisatie;
  licentievorm: "commercieel" | "open_source" | "saas" | "anders";
  open_source_licentie: string;
  website_url: string;
  documentatie_url: string;
  cloud_provider: string;
  aantal_gebruikers: number;
  gemma_componenten?: GemmaComponent[];
}

export interface PakketGebruik {
  id: string;
  /** UUID van het gekoppelde Pakket */
  pakket: string;
  pakket_naam: string;
  /** UUID van de Organisatie */
  organisatie: string;
  organisatie_naam: string;
  status: "in_gebruik" | "gepland" | "gestopt";
  status_display: string;
  start_datum: string | null;
  eind_datum: string | null;
  notitie: string;
  aangemaakt_op: string;
  gewijzigd_op: string;
}

export interface Standaard {
  id: string;
  naam: string;
  type: "verplicht" | "aanbevolen" | "optioneel";
  versie: string;
  beschrijving: string;
  forum_standaardisatie_url: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/** Invoervelden voor aanmaken of bijwerken van een pakket */
export interface PakketInput {
  naam: string;
  versie?: string;
  beschrijving?: string;
  licentievorm: "commercieel" | "open_source" | "saas" | "anders";
  open_source_licentie?: string;
  website_url?: string;
  documentatie_url?: string;
  cloud_provider?: string;
  leverancier?: string; // UUID — automatisch ingesteld vanuit user.organisatie
}
