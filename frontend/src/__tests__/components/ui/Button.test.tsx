import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button } from "@/components/ui/Button";

describe("Button", () => {
  it("rendert tekst correct", () => {
    render(<Button>Klik hier</Button>);
    expect(screen.getByRole("button", { name: "Klik hier" })).toBeInTheDocument();
  });

  it("roept onClick aan bij klik", async () => {
    const user = userEvent.setup();
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Klik</Button>);
    await user.click(screen.getByRole("button"));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("is uitgeschakeld wanneer disabled", () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("past primary variant class toe (standaard)", () => {
    render(<Button>Primary</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("bg-primary-500");
  });

  it("past outline variant class toe", () => {
    render(<Button variant="outline">Outline</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("border");
  });

  it("past danger variant class toe", () => {
    render(<Button variant="danger">Verwijderen</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("bg-red-600");
  });

  it("past size sm class toe", () => {
    render(<Button size="sm">Klein</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("h-8");
  });

  it("past size lg class toe", () => {
    render(<Button size="lg">Groot</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("h-12");
  });

  it("voegt custom className samen", () => {
    render(<Button className="extra-class">Test</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("extra-class");
  });
});
