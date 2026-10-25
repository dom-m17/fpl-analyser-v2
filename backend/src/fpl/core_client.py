import csv
import io
import os

import httpx

DEFAULT_BASE = "https://raw.githubusercontent.com/olbauday/FPL-Core-Insights/main/data"
SEASON = "2026-2027"
_HEADERS = {"User-Agent": "fpl-analyser-v2 (local)"}


class CoreError(Exception):
    pass


def fetch_tables() -> tuple[list[dict], list[dict]]:
    """Fetch players.csv and playerstats.csv from FPL-Core-Insights. Retries three times, then fails."""
    base = os.environ.get("CORE_BASE_URL", DEFAULT_BASE).rstrip("/")
    last: Exception | None = None
    for _ in range(3):
        try:
            with httpx.Client(timeout=30.0, headers=_HEADERS) as client:
                players = _get_csv(client, f"{base}/{SEASON}/players.csv")
                playerstats = _get_csv(client, f"{base}/{SEASON}/playerstats.csv")
            if not players or not playerstats:
                raise CoreError("empty FPL-Core-Insights table")
            return players, playerstats
        except (httpx.HTTPError, CoreError) as exc:
            last = exc
    raise CoreError("FPL-Core-Insights unavailable") from last


def _get_csv(client: httpx.Client, url: str) -> list[dict]:
    response = client.get(url)
    response.raise_for_status()
    return list(csv.DictReader(io.StringIO(response.text)))
