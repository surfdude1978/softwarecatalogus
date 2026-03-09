"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import {
  X,
  HelpCircle,
  Search,
  BookOpen,
  ChevronDown,
  ChevronRight,
  MapPin,
} from "lucide-react";
import { useHelp } from "@/hooks/use-help";
import {
  HELP_SECTIES,
  HelpSectie,
  getGroepen,
  getSectiesVoorRoute,
  zoekInHandleiding,
} from "@/data/handleiding-content";
import { MiniMarkdown } from "./MiniMarkdown";
import { HelpAI } from "./HelpAI";

// ──────────────────────────────────────────────────────────────
// Sectie-kaart
// ──────────────────────────────────────────────────────────────

function SectieKaart({
  sectie,
  standaard = false,
}: {
  sectie: HelpSectie;
  standaard?: boolean;
}) {
  const [open, setOpen] = useState(standaard);

  return (
    <div className="overflow-hidden rounded-lg border border-gray-100 bg-white shadow-sm">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-2 px-3 py-2.5 text-left hover:bg-gray-50"
        aria-expanded={open}
      >
        <span className="text-xs font-medium text-gray-800">{sectie.titel}</span>
        {open ? (
          <ChevronDown className="h-3.5 w-3.5 shrink-0 text-gray-400" />
        ) : (
          <ChevronRight className="h-3.5 w-3.5 shrink-0 text-gray-400" />
        )}
      </button>
      {open && (
        <div className="border-t border-gray-100 px-3 py-3">
          <MiniMarkdown content={sectie.inhoud} />
        </div>
      )}
    </div>
  );
}

// ──────────────────────────────────────────────────────────────
// Hoofd-drawer
// ──────────────────────────────────────────────────────────────

type TabId = "context" | "zoeken" | "ai";

export function HelpDrawer() {
  const { isOpen, open, close } = useHelp();
  const pathname = usePathname();
  const [actieveTab, setActieveTab] = useState<TabId>("context");
  const [zoekTerm, setZoekTerm] = useState("");

  // Bepaal context-secties op basis van huidige route
  const contextSecties = getSectiesVoorRoute(pathname ?? "");

  // Zoekresultaten
  const zoekResultaten =
    zoekTerm.length >= 2 ? zoekInHandleiding(zoekTerm) : [];

  // Schakel over naar context-tab als de pagina wisselt
  useEffect(() => {
    if (contextSecties.length > 0) setActieveTab("context");
  }, [pathname]); // eslint-disable-line react-hooks/exhaustive-deps

  // Sluit op Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) close();
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [isOpen, close]);

  const groepen = getGroepen();

  const tabs: { id: TabId; label: string; icon: React.ReactNode }[] = [
    {
      id: "context",
      label: "Voor u",
      icon: <MapPin className="h-3.5 w-3.5" />,
    },
    {
      id: "zoeken",
      label: "Zoeken",
      icon: <Search className="h-3.5 w-3.5" />,
    },
    {
      id: "ai",
      label: "AI",
      icon: (
        <span className="text-[11px] font-bold leading-none">✨</span>
      ),
    },
  ];

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/20 backdrop-blur-[1px]"
          onClick={close}
          aria-hidden="true"
        />
      )}

      {/* Drawer */}
      <aside
        role="dialog"
        aria-modal="true"
        aria-label="Help en handleiding"
        className={`fixed right-0 top-0 z-50 flex h-full w-full max-w-sm flex-col bg-white shadow-2xl transition-transform duration-300 ease-in-out ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* ── Header ── */}
        <div className="flex shrink-0 items-center justify-between border-b border-gray-100 bg-primary-600 px-4 py-3">
          <div className="flex items-center gap-2">
            <BookOpen className="h-4 w-4 text-white/80" />
            <span className="text-sm font-semibold text-white">
              Help &amp; Handleiding
            </span>
          </div>
          <button
            onClick={close}
            className="rounded-md p-1 text-white/70 hover:bg-primary-700 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white"
            aria-label="Sluit help"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* ── Tabs ── */}
        <div className="flex shrink-0 border-b border-gray-100">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActieveTab(tab.id)}
              className={`flex flex-1 items-center justify-center gap-1.5 py-2.5 text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-inset focus-visible:ring-2 focus-visible:ring-primary-500 ${
                actieveTab === tab.id
                  ? "border-b-2 border-primary-500 text-primary-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
              aria-selected={actieveTab === tab.id}
              aria-controls={`helptab-${tab.id}`}
              role="tab"
            >
              {tab.icon}
              {tab.label}
              {tab.id === "context" && contextSecties.length > 0 && (
                <span className="ml-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary-100 text-[9px] font-bold text-primary-700">
                  {contextSecties.length}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* ── Scrollbare inhoud ── */}
        <div className="flex-1 overflow-y-auto">
          {/* === Tab: Voor u (context) === */}
          {actieveTab === "context" && (
            <div
              id="helptab-context"
              role="tabpanel"
              className="p-4 space-y-3"
            >
              {contextSecties.length > 0 ? (
                <>
                  <p className="text-[10px] font-medium uppercase tracking-wide text-gray-400">
                    Hulp voor deze pagina
                  </p>
                  {contextSecties.map((s) => (
                    <SectieKaart key={s.id} sectie={s} standaard />
                  ))}
                  <div className="border-t border-gray-100 pt-3">
                    <p className="mb-2 text-[10px] font-medium uppercase tracking-wide text-gray-400">
                      Alle onderwerpen
                    </p>
                    {groepen.map((groep) => {
                      const secties = HELP_SECTIES.filter(
                        (s) =>
                          s.groep === groep &&
                          !contextSecties.find((c) => c.id === s.id)
                      );
                      if (secties.length === 0) return null;
                      return (
                        <div key={groep} className="mb-3">
                          <p className="mb-1.5 text-[10px] font-medium text-gray-400">
                            {groep}
                          </p>
                          <div className="space-y-1.5">
                            {secties.map((s) => (
                              <SectieKaart key={s.id} sectie={s} />
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </>
              ) : (
                <>
                  <p className="text-xs text-gray-500">
                    Geen specifieke helponderwerpen voor deze pagina. Bekijk alle
                    beschikbare onderwerpen hieronder.
                  </p>
                  {groepen.map((groep) => {
                    const secties = HELP_SECTIES.filter(
                      (s) => s.groep === groep
                    );
                    return (
                      <div key={groep} className="mb-3">
                        <p className="mb-1.5 text-[10px] font-medium uppercase tracking-wide text-gray-400">
                          {groep}
                        </p>
                        <div className="space-y-1.5">
                          {secties.map((s) => (
                            <SectieKaart key={s.id} sectie={s} />
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </>
              )}
            </div>
          )}

          {/* === Tab: Zoeken === */}
          {actieveTab === "zoeken" && (
            <div
              id="helptab-zoeken"
              role="tabpanel"
              className="p-4 space-y-3"
            >
              <div className="relative">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-gray-400" />
                <input
                  type="search"
                  value={zoekTerm}
                  onChange={(e) => setZoekTerm(e.target.value)}
                  placeholder="Zoek in de handleiding…"
                  className="w-full rounded-lg border border-gray-200 bg-gray-50 py-2 pl-9 pr-3 text-xs placeholder-gray-400 focus:border-primary-400 focus:bg-white focus:outline-none focus:ring-1 focus:ring-primary-400"
                  autoFocus
                  aria-label="Zoek in de handleiding"
                />
              </div>

              {zoekTerm.length > 0 && zoekTerm.length < 2 && (
                <p className="text-xs text-gray-400">
                  Typ minimaal 2 tekens om te zoeken.
                </p>
              )}

              {zoekTerm.length >= 2 && zoekResultaten.length === 0 && (
                <div className="rounded-lg bg-gray-50 p-4 text-center">
                  <p className="text-xs text-gray-500">
                    Geen resultaten gevonden voor{" "}
                    <strong className="text-gray-700">&quot;{zoekTerm}&quot;</strong>.
                  </p>
                  <p className="mt-1 text-xs text-gray-400">
                    Probeer de AI-assistent voor een directe vraag.
                  </p>
                </div>
              )}

              {zoekResultaten.length > 0 && (
                <>
                  <p className="text-[10px] text-gray-400">
                    {zoekResultaten.length}{" "}
                    {zoekResultaten.length === 1 ? "resultaat" : "resultaten"}
                  </p>
                  <div className="space-y-1.5">
                    {zoekResultaten.map((s) => (
                      <SectieKaart key={s.id} sectie={s} standaard />
                    ))}
                  </div>
                </>
              )}

              {zoekTerm.length === 0 && (
                <div className="space-y-3">
                  <p className="text-xs text-gray-500">
                    Zoek door alle {HELP_SECTIES.length} helponderwerpen.
                  </p>
                  {/* Populaire zoektermen */}
                  <div>
                    <p className="mb-2 text-[10px] font-medium uppercase tracking-wide text-gray-400">
                      Populaire onderwerpen
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {[
                        "pakket toevoegen",
                        "inloggen",
                        "2FA",
                        "architectuurkaart",
                        "exporteren",
                        "fiatteren",
                        "GEMMA",
                        "koppeling",
                      ].map((term) => (
                        <button
                          key={term}
                          onClick={() => setZoekTerm(term)}
                          className="rounded-full border border-gray-200 bg-white px-2.5 py-1 text-[11px] text-gray-600 hover:border-primary-300 hover:bg-primary-50 hover:text-primary-700"
                        >
                          {term}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* === Tab: AI === */}
          {actieveTab === "ai" && (
            <div
              id="helptab-ai"
              role="tabpanel"
              className="p-4"
            >
              <HelpAI paginaContext={pathname ?? ""} />
            </div>
          )}
        </div>

        {/* ── Footer ── */}
        <div className="shrink-0 border-t border-gray-100 px-4 py-2.5">
          <a
            href="/handleiding"
            className="flex items-center gap-1.5 text-[11px] text-gray-400 hover:text-primary-600"
          >
            <BookOpen className="h-3 w-3" />
            Volledige handleiding openen
          </a>
        </div>
      </aside>

      {/* Floating help-knop (zichtbaar als drawer dicht is) */}
      {!isOpen && (
        <button
          onClick={() => {
            setActieveTab(contextSecties.length > 0 ? "context" : "zoeken");
            open();
          }}
          className="fixed bottom-6 right-6 z-40 flex h-12 w-12 items-center justify-center rounded-full bg-primary-600 text-white shadow-lg ring-2 ring-white transition hover:bg-primary-700 hover:scale-105 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2"
          aria-label="Open help en handleiding"
          title="Help & Handleiding"
        >
          <HelpCircle className="h-5 w-5" />
        </button>
      )}
    </>
  );
}
