import { cn } from "@/lib/utils";

describe("cn", () => {
  it("combineert meerdere classes", () => {
    expect(cn("text-red-500", "font-bold")).toBe("text-red-500 font-bold");
  });

  it("merged conflicterende Tailwind classes", () => {
    expect(cn("text-red-500", "text-blue-500")).toBe("text-blue-500");
  });

  it("filtert falsy waarden", () => {
    expect(cn("base", false && "hidden", undefined, null, "extra")).toBe("base extra");
  });

  it("handelt conditionele objecten af", () => {
    expect(cn("base", { "text-red-500": true, "text-blue-500": false })).toBe(
      "base text-red-500"
    );
  });

  it("retourneert lege string zonder input", () => {
    expect(cn()).toBe("");
  });
});
