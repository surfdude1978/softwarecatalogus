import { ApiError } from "@/lib/api";

// ─────────────────────────────────────────────────────────────────────────────
// Hulpfunctie: maak een ApiError aan met een gegeven body-string.
// ─────────────────────────────────────────────────────────────────────────────

function maakApiError(status: number, body: string): ApiError {
  return new ApiError(status, body);
}

// ─────────────────────────────────────────────────────────────────────────────
// ApiError — basisgedrag
// ─────────────────────────────────────────────────────────────────────────────

describe("ApiError — constructor", () => {
  it("slaat status en body op", () => {
    const err = maakApiError(400, '{"detail":"fout"}');
    expect(err.status).toBe(400);
    expect(err.body).toBe('{"detail":"fout"}');
    expect(err.name).toBe("ApiError");
  });

  it("is een instantie van Error", () => {
    const err = maakApiError(500, "Server error");
    expect(err).toBeInstanceOf(Error);
    expect(err).toBeInstanceOf(ApiError);
  });

  it("bevat status en body in het message-veld", () => {
    const err = maakApiError(404, "Not Found");
    expect(err.message).toContain("404");
    expect(err.message).toContain("Not Found");
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// ApiError.parseBody()
// ─────────────────────────────────────────────────────────────────────────────

describe("ApiError.parseBody()", () => {
  it("parsed geldige JSON met object terug", () => {
    const err = maakApiError(400, '{"detail":"Ongeldig"}');
    expect(err.parseBody()).toEqual({ detail: "Ongeldig" });
  });

  it("geeft null terug bij HTML (geen JSON)", () => {
    const err = maakApiError(500, "<html><body>Server Error</body></html>");
    expect(err.parseBody()).toBeNull();
  });

  it("geeft null terug bij plain text", () => {
    const err = maakApiError(503, "Service Unavailable");
    expect(err.parseBody()).toBeNull();
  });

  it("geeft null terug bij lege body", () => {
    const err = maakApiError(204, "");
    expect(err.parseBody()).toBeNull();
  });

  it("geeft null terug bij body met alleen witruimte", () => {
    const err = maakApiError(400, "   ");
    expect(err.parseBody()).toBeNull();
  });

  it("geeft null terug als JSON geen object is (array)", () => {
    const err = maakApiError(400, '["a","b"]');
    expect(err.parseBody()).toBeNull();
  });

  it("geeft null terug als JSON geen object is (getal)", () => {
    const err = maakApiError(400, "42");
    expect(err.parseBody()).toBeNull();
  });

  it("geeft null terug als JSON geen object is (string)", () => {
    const err = maakApiError(400, '"een string"');
    expect(err.parseBody()).toBeNull();
  });

  it("geeft null terug bij ongeldige JSON-fragment", () => {
    const err = maakApiError(400, "{ongeldige json}");
    expect(err.parseBody()).toBeNull();
  });

  it("parsed JSON met meerdere velden correct", () => {
    const err = maakApiError(400, '{"naam":["Dit veld is verplicht."],"email":["Ongeldig e-mailadres."]}');
    expect(err.parseBody()).toEqual({
      naam: ["Dit veld is verplicht."],
      email: ["Ongeldig e-mailadres."],
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// ApiError.getDetail()
// ─────────────────────────────────────────────────────────────────────────────

describe("ApiError.getDetail()", () => {
  it("geeft detail-veld terug uit JSON body", () => {
    const err = maakApiError(401, '{"detail":"Ongeldige inloggegevens."}');
    expect(err.getDetail()).toBe("Ongeldige inloggegevens.");
  });

  it("geeft de opgegeven fallback terug bij HTML body", () => {
    const err = maakApiError(500, "<html>Error</html>");
    expect(err.getDetail("Serverfout.")).toBe("Serverfout.");
  });

  it("geeft de opgegeven fallback terug bij lege body", () => {
    const err = maakApiError(400, "");
    expect(err.getDetail("Fallback bericht")).toBe("Fallback bericht");
  });

  it("geeft de standaard fallback terug als geen fallback opgegeven", () => {
    const err = maakApiError(400, "geen json");
    expect(err.getDetail()).toBe("Er is een fout opgetreden.");
  });

  it("geeft fallback terug als detail-veld ontbreekt in JSON", () => {
    const err = maakApiError(400, '{"naam":["Dit veld is verplicht."]}');
    expect(err.getDetail("Standaard fout.")).toBe("Standaard fout.");
  });

  it("geeft fallback terug als detail leeg is", () => {
    const err = maakApiError(400, '{"detail":""}');
    expect(err.getDetail("Fallback")).toBe("Fallback");
  });

  it("geeft fallback terug als detail geen string is", () => {
    const err = maakApiError(400, '{"detail":["lijst fout"]}');
    expect(err.getDetail("Fallback")).toBe("Fallback");
  });

  it("geeft detail terug bij 403 status", () => {
    const err = maakApiError(403, '{"detail":"Twee-factor verificatie vereist."}');
    expect(err.getDetail("Geen toegang.")).toBe("Twee-factor verificatie vereist.");
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// ApiError.getFieldErrors()
// ─────────────────────────────────────────────────────────────────────────────

describe("ApiError.getFieldErrors()", () => {
  it("geeft veldfouten terug uit DRF-formaat (arrays)", () => {
    const err = maakApiError(
      400,
      '{"naam":["Dit veld is verplicht."],"email":["Ongeldig e-mailadres."]}'
    );
    expect(err.getFieldErrors()).toEqual({
      naam: ["Dit veld is verplicht."],
      email: ["Ongeldig e-mailadres."],
    });
  });

  it("geeft veldfouten terug als veld een string is (niet array)", () => {
    const err = maakApiError(400, '{"naam":"Dit veld is verplicht."}');
    expect(err.getFieldErrors()).toEqual({
      naam: ["Dit veld is verplicht."],
    });
  });

  it("slaat het detail-veld over", () => {
    const err = maakApiError(400, '{"detail":"Fout.","naam":["Verplicht."]}');
    const fouten = err.getFieldErrors();
    expect(fouten).not.toHaveProperty("detail");
    expect(fouten).toHaveProperty("naam");
  });

  it("geeft leeg object terug bij HTML body", () => {
    const err = maakApiError(500, "<html>Error</html>");
    expect(err.getFieldErrors()).toEqual({});
  });

  it("geeft leeg object terug bij lege body", () => {
    const err = maakApiError(400, "");
    expect(err.getFieldErrors()).toEqual({});
  });

  it("geeft leeg object terug als body alleen detail bevat", () => {
    const err = maakApiError(400, '{"detail":"Alleen een detail bericht."}');
    expect(err.getFieldErrors()).toEqual({});
  });

  it("geeft meerdere berichten per veld terug", () => {
    const err = maakApiError(
      400,
      '{"wachtwoord":["Te kort.","Bevat geen hoofdletter.","Bevat geen cijfer."]}'
    );
    expect(err.getFieldErrors()).toEqual({
      wachtwoord: ["Te kort.", "Bevat geen hoofdletter.", "Bevat geen cijfer."],
    });
  });

  it("converteert niet-string array-waarden naar strings", () => {
    // DRF kan soms integers of booleans sturen — worden geconverteerd via String()
    const err = maakApiError(400, '{"veld":[1,true,"tekst"]}');
    expect(err.getFieldErrors()).toEqual({
      veld: ["1", "true", "tekst"],
    });
  });

  it("negeert velden met waarden die geen string of array zijn", () => {
    const err = maakApiError(400, '{"getal":42,"geldig":["fout"]}');
    const fouten = err.getFieldErrors();
    expect(fouten).not.toHaveProperty("getal");
    expect(fouten).toHaveProperty("geldig");
  });
});
