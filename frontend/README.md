# SafeFlow AI — Frontend

React + Vite SPA that integrates with the FastAPI backend at `http://localhost:8000`.

## Setup

```bash
cd frontend
npm install
npm run dev
```

Vite serves on `http://localhost:5173` and proxies `/auth` and `/api` to the
backend. Start the backend separately with:

```bash
uv run uvicorn app.main:app --reload
```

## Demo flow (two browser windows)

Open two browser windows (e.g. one regular, one private/incognito) and log in
as different users — one will be the **sender**, the other the **receiver**.
Submit a transfer from the sender's window using the receiver's IBAN; both
dashboards refresh every 5 seconds, so balances and transaction lists update
live.

Risk evaluation is fully driven by the backend:

- `LOW` risk → backend auto-settles → **Transaction Approved** screen.
- `MEDIUM` risk → status `WARNED` → **Proceed Cautiously** screen, requires the
  sender's password to confirm and settle.
- `HIGH` risk → status `REJECTED` → **Transaction Blocked** screen.

## Theming

All colors, fonts, spacing and radii live as CSS custom properties in
`src/styles/theme.css`. Per-component styles use CSS Modules
(`*.module.css`).
