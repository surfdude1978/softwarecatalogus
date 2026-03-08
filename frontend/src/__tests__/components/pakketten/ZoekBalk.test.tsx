import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ZoekBalk } from "@/components/pakketten/ZoekBalk";

describe("ZoekBalk", () => {
  it("rendert de zoekbalk met role search", () => {
    render(<ZoekBalk onSearch={jest.fn()} />);
    expect(screen.getByRole("search")).toBeInTheDocument();
  });

  it("heeft een toegankelijke aria-label", () => {
    render(<ZoekBalk onSearch={jest.fn()} />);
    expect(screen.getByLabelText("Zoeken in de catalogus")).toBeInTheDocument();
  });

  it("toont standaard placeholder", () => {
    render(<ZoekBalk onSearch={jest.fn()} />);
    expect(screen.getByPlaceholderText("Zoek pakketten...")).toBeInTheDocument();
  });

  it("toont custom placeholder", () => {
    render(<ZoekBalk onSearch={jest.fn()} placeholder="Zoek organisaties..." />);
    expect(screen.getByPlaceholderText("Zoek organisaties...")).toBeInTheDocument();
  });

  it("roept onSearch aan bij submit", async () => {
    const user = userEvent.setup();
    const handleSearch = jest.fn();
    render(<ZoekBalk onSearch={handleSearch} />);

    const input = screen.getByLabelText("Zoeken in de catalogus");
    await user.type(input, "zaaksysteem");
    await user.click(screen.getByText("Zoeken"));

    expect(handleSearch).toHaveBeenCalledWith("zaaksysteem");
  });

  it("roept onSearch aan bij Enter", async () => {
    const user = userEvent.setup();
    const handleSearch = jest.fn();
    render(<ZoekBalk onSearch={handleSearch} />);

    const input = screen.getByLabelText("Zoeken in de catalogus");
    await user.type(input, "burgerzaken{Enter}");

    expect(handleSearch).toHaveBeenCalledWith("burgerzaken");
  });

  it("toont standaard waarde", () => {
    render(<ZoekBalk onSearch={jest.fn()} defaultValue="test query" />);
    const input = screen.getByLabelText("Zoeken in de catalogus") as HTMLInputElement;
    expect(input.value).toBe("test query");
  });
});
