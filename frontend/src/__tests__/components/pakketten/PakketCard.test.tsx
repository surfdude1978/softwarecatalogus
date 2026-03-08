import { render, screen } from "@testing-library/react";
import { PakketCard } from "@/components/pakketten/PakketCard";

// Mock next/link
jest.mock("next/link", () => {
  return function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return <a href={href}>{children}</a>;
  };
});

const basePakket = {
  id: "test-uuid-1",
  naam: "Suite4Gemeenten",
  versie: "5.0",
  status: "actief",
  beschrijving: "Compleet pakket voor gemeentelijke dienstverlening.",
  leverancier_naam: "Centric",
  licentievorm: "saas",
  aantal_gebruikers: 42,
};

describe("PakketCard", () => {
  it("toont de naam van het pakket", () => {
    render(<PakketCard pakket={basePakket} />);
    expect(screen.getByText("Suite4Gemeenten")).toBeInTheDocument();
  });

  it("toont de versie", () => {
    render(<PakketCard pakket={basePakket} />);
    expect(screen.getByText("v5.0")).toBeInTheDocument();
  });

  it("toont de status badge", () => {
    render(<PakketCard pakket={basePakket} />);
    expect(screen.getByText("actief")).toBeInTheDocument();
  });

  it("toont de beschrijving", () => {
    render(<PakketCard pakket={basePakket} />);
    expect(screen.getByText(/gemeentelijke dienstverlening/)).toBeInTheDocument();
  });

  it("toont de leverancier naam", () => {
    render(<PakketCard pakket={basePakket} />);
    expect(screen.getByText("Centric")).toBeInTheDocument();
  });

  it("toont het aantal gemeenten", () => {
    render(<PakketCard pakket={basePakket} />);
    expect(screen.getByText("42 gemeenten")).toBeInTheDocument();
  });

  it("toont licentievorm label", () => {
    render(<PakketCard pakket={basePakket} />);
    expect(screen.getByText("SaaS")).toBeInTheDocument();
  });

  it("linkt naar de detailpagina", () => {
    render(<PakketCard pakket={basePakket} />);
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/pakketten/test-uuid-1");
  });

  it("toont fallback beschrijving als leeg", () => {
    const pakket = { ...basePakket, beschrijving: "" };
    render(<PakketCard pakket={pakket} />);
    expect(screen.getByText("Geen beschrijving beschikbaar.")).toBeInTheDocument();
  });

  it("toont fallback leverancier als onbekend", () => {
    const pakket = { ...basePakket, leverancier_naam: undefined, leverancier: null };
    render(<PakketCard pakket={pakket} />);
    expect(screen.getByText("Onbekend")).toBeInTheDocument();
  });

  it("verbergt versie als niet aanwezig", () => {
    const pakket = { ...basePakket, versie: undefined };
    render(<PakketCard pakket={pakket} />);
    expect(screen.queryByText(/^v/)).not.toBeInTheDocument();
  });
});
