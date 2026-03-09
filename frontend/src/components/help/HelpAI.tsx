"use client";

import { useState, useRef, useEffect } from "react";
import { Bot, Send, Loader2, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import { MiniMarkdown } from "./MiniMarkdown";

interface Bericht {
  rol: "gebruiker" | "assistent";
  tekst: string;
}

interface HelpAIProps {
  paginaContext: string;
}

export function HelpAI({ paginaContext }: HelpAIProps) {
  const [berichten, setBerichten] = useState<Bericht[]>([]);
  const [invoer, setInvoer] = useState("");
  const [isLaden, setIsLaden] = useState(false);
  const [aiNietBeschikbaar, setAiNietBeschikbaar] = useState(false);
  const lijstRef = useRef<HTMLDivElement>(null);

  // Scroll naar beneden bij nieuw bericht
  useEffect(() => {
    if (lijstRef.current) {
      lijstRef.current.scrollTop = lijstRef.current.scrollHeight;
    }
  }, [berichten]);

  const verstuur = async () => {
    const vraag = invoer.trim();
    if (!vraag || isLaden) return;

    setInvoer("");
    setBerichten((prev) => [...prev, { rol: "gebruiker", tekst: vraag }]);
    setIsLaden(true);

    try {
      const data = await api.post<{ antwoord: string }>(
        "/api/v1/help/vraag/",
        { vraag, context: paginaContext }
      );
      setBerichten((prev) => [
        ...prev,
        { rol: "assistent", tekst: data.antwoord },
      ]);
    } catch (err: unknown) {
      const status = (err as { status?: number })?.status;
      if (status === 503) {
        setAiNietBeschikbaar(true);
        setBerichten((prev) => [
          ...prev,
          {
            rol: "assistent",
            tekst: "De AI-assistent is momenteel niet beschikbaar. Gebruik de zoekfunctie hierboven om antwoorden te vinden.",
          },
        ]);
      } else {
        setBerichten((prev) => [
          ...prev,
          {
            rol: "assistent",
            tekst: "Er is een fout opgetreden. Probeer het later opnieuw.",
          },
        ]);
      }
    } finally {
      setIsLaden(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      verstuur();
    }
  };

  return (
    <div className="flex flex-col">
      {/* Header */}
      <div className="mb-3 flex items-center gap-2">
        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-primary-500 to-primary-700">
          <Bot className="h-3.5 w-3.5 text-white" />
        </div>
        <span className="text-xs font-medium text-gray-700">
          AI-assistent
        </span>
        <span className="rounded-full bg-primary-100 px-1.5 py-0.5 text-[10px] font-medium text-primary-700">
          beta
        </span>
      </div>

      {/* Niet beschikbaar melding */}
      {aiNietBeschikbaar && berichten.length === 0 && (
        <div className="mb-3 flex items-start gap-2 rounded-md bg-amber-50 p-2.5 text-xs text-amber-800">
          <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <span>
            AI niet geconfigureerd. Stel{" "}
            <code className="rounded bg-amber-100 px-1 font-mono text-[10px]">
              ANTHROPIC_API_KEY
            </code>{" "}
            in om de AI-assistent te activeren.
          </span>
        </div>
      )}

      {/* Berichten */}
      {berichten.length > 0 && (
        <div
          ref={lijstRef}
          className="mb-3 max-h-56 space-y-3 overflow-y-auto rounded-lg bg-gray-50 p-3"
        >
          {berichten.map((b, idx) => (
            <div
              key={idx}
              className={`flex gap-2 ${
                b.rol === "gebruiker" ? "flex-row-reverse" : "flex-row"
              }`}
            >
              {b.rol === "assistent" && (
                <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary-500">
                  <Bot className="h-3 w-3 text-white" />
                </div>
              )}
              <div
                className={`max-w-[85%] rounded-lg px-3 py-2 text-xs ${
                  b.rol === "gebruiker"
                    ? "bg-primary-500 text-white"
                    : "bg-white shadow-sm text-gray-700"
                }`}
              >
                {b.rol === "assistent" ? (
                  <MiniMarkdown content={b.tekst} />
                ) : (
                  b.tekst
                )}
              </div>
            </div>
          ))}

          {/* Laad-indicator */}
          {isLaden && (
            <div className="flex items-center gap-2">
              <div className="flex h-5 w-5 items-center justify-center rounded-full bg-primary-500">
                <Bot className="h-3 w-3 text-white" />
              </div>
              <div className="flex gap-1 rounded-lg bg-white px-3 py-2 shadow-sm">
                {[0, 1, 2].map((n) => (
                  <span
                    key={n}
                    className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary-400"
                    style={{ animationDelay: `${n * 150}ms` }}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Invoer */}
      <div className="flex gap-2">
        <input
          type="text"
          value={invoer}
          onChange={(e) => setInvoer(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            berichten.length === 0
              ? "Stel een vraag over de Softwarecatalogus…"
              : "Stel een vervolgvraag…"
          }
          disabled={isLaden}
          className="flex-1 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-xs placeholder-gray-400 focus:border-primary-400 focus:bg-white focus:outline-none focus:ring-1 focus:ring-primary-400 disabled:opacity-50"
          aria-label="Stel een vraag aan de AI-assistent"
        />
        <button
          onClick={verstuur}
          disabled={!invoer.trim() || isLaden}
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary-500 text-white transition hover:bg-primary-600 disabled:opacity-40"
          aria-label="Verstuur vraag"
        >
          {isLaden ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Send className="h-3.5 w-3.5" />
          )}
        </button>
      </div>

      {/* Hulptekst */}
      {berichten.length === 0 && !aiNietBeschikbaar && (
        <p className="mt-2 text-[10px] text-gray-400">
          Bijv: &quot;Hoe voeg ik een pakket toe?&quot; of &quot;Wat is het verschil
          tussen gebruik-beheerder en raadpleger?&quot;
        </p>
      )}
    </div>
  );
}
