# FPL Analyser

A local dashboard of official Fantasy Premier League fixture difficulty. The first page is a ticker: 20 teams × the next 4, 6, or 8 gameweeks, ranked by average FDR. It does not recommend transfers.

Not affiliated with the Premier League or Fantasy Premier League. Reads only public endpoints.

## Stack

- Backend: Python 3.12+, FastAPI, httpx
- Frontend: React, TypeScript, Vite

## Local setup

```sh
cd backend
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/uvicorn fpl.api:app --reload
```

```sh
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Vite proxies `/api` to the backend on port 8000.

Optional environment variables (backend):

- `FPL_BASE_URL` — default `https://fantasy.premierleague.com/api`
- `CORS_ORIGIN` — default `http://localhost:5173`

## Tests

```sh
cd backend && .venv/bin/python -m pytest
```

No network. The suite checks the ticker transform against small hand-built payloads and one committed FPL snapshot.

## What this is not (yet)

Player stats, expected points, squad import, accounts, or a hosted deploy.
