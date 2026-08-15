import os

import httpx

DEFAULT_BASE = "https://fantasy.premierleague.com/api"
_HEADERS = {"User-Agent": "fpl-analyser-v2 (local)"}


class FPLError(Exception):
    pass


def fetch_payloads() -> tuple[dict, list]:
    """Fetch bootstrap-static and fixtures. Retries three times, then fails."""
    base = os.environ.get("FPL_BASE_URL", DEFAULT_BASE).rstrip("/")
    last: Exception | None = None
    for _ in range(3):
        try:
            with httpx.Client(timeout=20.0, headers=_HEADERS) as client:
                bootstrap = _get_json(client, f"{base}/bootstrap-static/")
                fixtures = _get_json(client, f"{base}/fixtures/")
            if not isinstance(bootstrap, dict) or not isinstance(fixtures, list):
                raise FPLError("unexpected FPL payload shape")
            return bootstrap, fixtures
        except (httpx.HTTPError, FPLError) as exc:
            last = exc
    raise FPLError("FPL API unavailable") from last


def _get_json(client: httpx.Client, url: str) -> object:
    response = client.get(url)
    response.raise_for_status()
    return response.json()
