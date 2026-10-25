# FPL Analyser

A local dashboard of official Fantasy Premier League fixture difficulty. It does not recommend transfers.

- **Fixtures** — a ticker: 20 teams × the next 4–8 gameweeks, ranked by average FDR.
- **Players** — every player with team, position, price, and their next 5 fixtures coloured by FDR. Search by name, filter by position.

Fixtures and difficulty come from the FPL API. Player lists and prices come from [FPL-Core-Insights](https://github.com/olbauday/FPL-Core-Insights) CSVs, which refresh twice a day.

Not affiliated with the Premier League or Fantasy Premier League. Reads only public endpoints.

## Stack

- Backend: Python 3.12+, FastAPI, httpx
- Frontend: React, TypeScript, Vite

## Run with Docker

Requires Docker with Compose. From the repo root:

```sh
docker compose up --build
```

Open http://localhost:8080. Stop with `docker compose down`.

This starts two containers under the `fpl` project:

- `fpl-frontend-1` — nginx serving the built React app on port 8080, forwarding `/api` to the backend (see `frontend/nginx.conf`)
- `fpl-backend-1` — the FastAPI app on port 8000, reachable only from the frontend container

## Local development

For hot reload, run each half in its own terminal:

```sh
cd backend && make run    # venv, install, uvicorn --reload on :8000
```

```sh
cd frontend && make run   # npm install, vite dev server on :5173
```

Open http://localhost:5173. Vite proxies `/api` to the backend on port 8000.

Optional environment variables (backend, local development):

- `FPL_BASE_URL` — default `https://fantasy.premierleague.com/api`
- `CORE_BASE_URL` — default `https://raw.githubusercontent.com/olbauday/FPL-Core-Insights/main/data`
- `CORS_ORIGIN` — default `http://localhost:5173`

## Tests

```sh
cd backend && .venv/bin/python -m pytest
```

No network. The suite checks the ticker and players transforms against small hand-built payloads and one committed FPL snapshot.

## What this is not (yet)

Player stats columns, sorting the players table, expected points, squad import, accounts, or a hosted deploy.
