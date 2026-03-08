import { render, screen } from "@testing-library/react";
import { Badge } from "@/components/ui/Badge";

describe("Badge", () => {
  it("rendert children", () => {
    render(<Badge>Actief</Badge>);
    expect(screen.getByText("Actief")).toBeInTheDocument();
  });

  it("past default variant toe", () => {
    render(<Badge>Default</Badge>);
    expect(screen.getByText("Default").className).toContain("bg-gray-100");
  });

  it("past success variant toe", () => {
    render(<Badge variant="success">OK</Badge>);
    expect(screen.getByText("OK").className).toContain("bg-green-100");
  });

  it("past warning variant toe", () => {
    render(<Badge variant="warning">Let op</Badge>);
    expect(screen.getByText("Let op").className).toContain("bg-yellow-100");
  });

  it("past danger variant toe", () => {
    render(<Badge variant="danger">Fout</Badge>);
    expect(screen.getByText("Fout").className).toContain("bg-red-100");
  });

  it("past info variant toe", () => {
    render(<Badge variant="info">Info</Badge>);
    expect(screen.getByText("Info").className).toContain("bg-blue-100");
  });

  it("accepteert custom className", () => {
    render(<Badge className="ml-2">Test</Badge>);
    expect(screen.getByText("Test").className).toContain("ml-2");
  });
});
