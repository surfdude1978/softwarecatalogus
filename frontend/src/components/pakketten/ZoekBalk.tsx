"use client";

import { useState, useCallback } from "react";
import { Input } from "@/components/ui/Input";

interface ZoekBalkProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  defaultValue?: string;
}

export function ZoekBalk({
  onSearch,
  placeholder = "Zoek pakketten...",
  defaultValue = "",
}: ZoekBalkProps) {
  const [value, setValue] = useState(defaultValue);

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      onSearch(value);
    },
    [value, onSearch]
  );

  return (
    <form onSubmit={handleSubmit} role="search" className="flex gap-2">
      <div className="flex-1">
        <Input
          id="zoek"
          type="search"
          placeholder={placeholder}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          aria-label="Zoeken in de catalogus"
        />
      </div>
      <button
        type="submit"
        className="rounded-md bg-primary-500 px-6 py-2 text-sm font-medium text-white hover:bg-primary-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2"
      >
        Zoeken
      </button>
    </form>
  );
}
