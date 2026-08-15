import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from fpl.cache import get_payloads
from fpl.client import FPLError
from fpl.ticker import ALLOWED_HORIZONS, Ticker, build_ticker

app = FastAPI(title="FPL Analyser")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("CORS_ORIGIN", "http://localhost:5173")],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/fixtures/ticker")
def fixture_ticker(horizon: int = Query(default=6)) -> Ticker:
    if horizon not in ALLOWED_HORIZONS:
        raise HTTPException(status_code=400, detail="horizon must be 4, 6, or 8")
    try:
        bootstrap, fixtures = get_payloads()
    except FPLError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return build_ticker(bootstrap, fixtures, horizon)
