"use client";

import { Select } from "@/components/ui/Select";

interface PakketFiltersProps {
  filters: {
    licentievorm: string;
    status: string;
    ordering: string;
  };
  onChange: (key: string, value: string) => void;
}

export function PakketFilters({ filters, onChange }: PakketFiltersProps) {
  return (
    <div className="flex flex-wrap gap-4">
      <Select
        id="filter-licentievorm"
        label="Licentievorm"
        placeholder="Alle licentievormen"
        value={filters.licentievorm}
        onChange={(e) => onChange("licentievorm", e.target.value)}
        options={[
          { value: "commercieel", label: "Commercieel" },
          { value: "open_source", label: "Open source" },
          { value: "saas", label: "SaaS" },
          { value: "anders", label: "Anders" },
        ]}
      />
      <Select
        id="filter-status"
        label="Status"
        placeholder="Alle statussen"
        value={filters.status}
        onChange={(e) => onChange("status", e.target.value)}
        options={[
          { value: "actief", label: "Actief" },
          { value: "concept", label: "Concept" },
        ]}
      />
      <Select
        id="filter-ordering"
        label="Sorteren op"
        value={filters.ordering}
        onChange={(e) => onChange("ordering", e.target.value)}
        options={[
          { value: "naam", label: "Naam (A-Z)" },
          { value: "-naam", label: "Naam (Z-A)" },
          { value: "-aantal_gebruikers", label: "Meest gebruikt" },
          { value: "-gewijzigd_op", label: "Recent bijgewerkt" },
        ]}
      />
    </div>
  );
}
