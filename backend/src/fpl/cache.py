import time

from fpl.client import FPLError, fetch_payloads

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
