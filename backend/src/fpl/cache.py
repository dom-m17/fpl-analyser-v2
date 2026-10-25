import time

from fpl.client import FPLError, fetch_payloads
from fpl.core_client import CoreError, fetch_tables

TTL_SECONDS = 30 * 60

_bootstrap: dict | None = None
_fixtures: list | None = None
_fetched_at: float = 0.0


def get_payloads() -> tuple[dict, list]:
    """Return cached FPL payloads, fetching when the TTL has expired.

    If a fetch fails and we already have data, the stale cache is returned.
    """
    global _bootstrap, _fixtures, _fetched_at
    now = time.monotonic()
    if _bootstrap is not None and _fixtures is not None and now - _fetched_at < TTL_SECONDS:
        return _bootstrap, _fixtures
    try:
        bootstrap, fixtures = fetch_payloads()
    except FPLError:
        if _bootstrap is not None and _fixtures is not None:
            return _bootstrap, _fixtures
        raise
    _bootstrap, _fixtures, _fetched_at = bootstrap, fixtures, now
    return bootstrap, fixtures


CORE_TTL_SECONDS = 6 * 60 * 60

_core_players: list | None = None
_core_playerstats: list | None = None
_core_fetched_at: float = 0.0


def get_core_tables() -> tuple[list, list]:
    """Return cached FPL-Core-Insights tables, fetching when the TTL has expired.

    The source refreshes twice a day. If a fetch fails and we already have data, the stale cache is returned.
    """
    global _core_players, _core_playerstats, _core_fetched_at
    now = time.monotonic()
    if (
        _core_players is not None
        and _core_playerstats is not None
        and now - _core_fetched_at < CORE_TTL_SECONDS
    ):
        return _core_players, _core_playerstats
    try:
        players, playerstats = fetch_tables()
    except CoreError:
        if _core_players is not None and _core_playerstats is not None:
            return _core_players, _core_playerstats
        raise
    _core_players, _core_playerstats, _core_fetched_at = players, playerstats, now
    return players, playerstats
