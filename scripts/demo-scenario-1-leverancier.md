# Demo 1: Leverancier registratie + fiattering

**Ingelogd als:** niemand (anoniem)
**Eindresultaat:** Pieter van Dijk (TechSolutions BV) kan inloggen

---

## Stap 1 – Registreer nieuwe organisatie + gebruiker

- Navigeer naar: `http://localhost:3000/registreer/organisatie`
- **Stap 1 – Organisatiegegevens:**
  - Naam: `TechSolutions BV`
  - Type: `Leverancier`
  - Website: `https://techsolutions.nl`
  - Klik **Volgende →**
- **Stap 2 – Accountgegevens:**
  - Naam: `Pieter van Dijk`
  - E-mail: `pieter@techsolutions.nl`
  - Wachtwoord: `Welkom12345!`
  - Klik **Registratie indienen**
- Toon succespagina ("Uw registratie is ontvangen")

---

## Stap 2 – Admin fiattert organisatie

- Navigeer naar: `http://localhost:3000/login`
- Login als: `admin@vngrealisatie.nl` / `Welkom01!`
- Navigeer naar: `/beheer/organisaties`
- Zie **"TechSolutions BV – Concept"** in de lijst
- Klik **Fiatteren** → verdwijnt uit de lijst

---

## Stap 3 – Admin fiattert gebruiker

- Navigeer naar: `/beheer/gebruikers`
- Zie **"Pieter van Dijk – Wacht op fiattering"**
- Klik **Fiatteren** → verdwijnt uit de lijst

---

## Stap 4 – Pieter logt in

- Klik **Uitloggen** in de navigatie
- Navigeer naar: `/login`
- Login als: `pieter@techsolutions.nl` / `Welkom12345!`
- Toon dashboard `/aanbod` (lege pakketlijst voor TechSolutions BV)
