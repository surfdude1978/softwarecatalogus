# Demo 2: Pakket aanmaken + goedkeuring door admin

**Ingelogd als:** Pieter van Dijk (`pieter@techsolutions.nl`)
**Eindresultaat:** "WijkBeheer Pro" is actief en zichtbaar in de publieke catalogus

---

## Stap 1 – Navigeer naar nieuw pakket

- Navigeer naar: `http://localhost:3000/aanbod`
- Klik **"+ Nieuw pakket"**

---

## Stap 2 – Vul pakketformulier in

- **Naam:** `WijkBeheer Pro`
- **Versie:** `3.0`
- **Beschrijving:** `Integraal beheer van de openbare ruimte voor gemeenten`
- **Licentievorm:** `SaaS`
- **Website:** `https://wijkbeheerpro.nl`
- **GEMMA-componenten:** selecteer `Zaaksysteem`
- Klik **"Pakket aanmaken"**

---

## Stap 3 – Toon concept-status

- Terug in `/aanbod`
- Zie **"WijkBeheer Pro"** in de lijst met badge **"Concept"**
- _(Pakket is nog NIET zichtbaar in de publieke catalogus)_

---

## Stap 4 – Admin fiattert pakket

- Klik **Uitloggen**
- Login als: `admin@vngrealisatie.nl` / `Welkom01!`
- Navigeer naar: `/beheer/pakketten`
- Zie **"WijkBeheer Pro v3.0 – Concept"** in de lijst
- Klik **Fiatteren** → verdwijnt uit de lijst (pakket is nu actief)

---

## Stap 5 – Toon in publieke catalogus

- Navigeer naar: `http://localhost:3000/pakketten`
- Zoek op: `WijkBeheer`
- Zie **"WijkBeheer Pro"** verschijnen _(nu actief, geen concept badge)_
