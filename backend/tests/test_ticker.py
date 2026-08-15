import json
from pathlib import Path

from fpl.ticker import CellFixture, build_ticker, start_event_id

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _event(event_id: int, *, current: bool = False, nxt: bool = False, finished: bool = False) -> dict:
    return {"id": event_id, "is_current": current, "is_next": nxt, "finished": finished}


def _team(team_id: int, name: str, short_name: str) -> dict:
    return {"id": team_id, "name": name, "short_name": short_name}


def _fixture(event: int | None, home: int, away: int, home_fdr: int, away_fdr: int) -> dict:
    return {
        "event": event,
        "team_h": home,
        "team_a": away,
        "team_h_difficulty": home_fdr,
        "team_a_difficulty": away_fdr,
    }


def _bootstrap(events: list[dict], teams: list[dict]) -> dict:
    return {"events": events, "teams": teams}


TEAMS = [
    _team(1, "Arsenal", "ARS"),
    _team(2, "Liverpool", "LIV"),
    _team(3, "Chelsea", "CHE"),
]


def test_window_starts_at_current_unfinished_event() -> None:
    events = [
        _event(1, current=True, finished=True),
        _event(2, current=True, finished=False),
        _event(3, nxt=True),
    ]
    assert start_event_id(events) == 2


def test_window_falls_back_to_next_when_no_current() -> None:
    events = [_event(1, nxt=True), _event(2), _event(3)]
    assert start_event_id(events) == 1


def test_finished_current_falls_back_to_next() -> None:
    events = [_event(1, current=True, finished=True), _event(2, nxt=True)]
    assert start_event_id(events) == 2


def test_horizon_slices_the_next_n_gameweeks() -> None:
    events = [_event(i, nxt=(i == 1)) for i in range(1, 12)]
    bootstrap = _bootstrap(events, TEAMS)
    fixtures = [_fixture(gw, 1, 2, 2, 4) for gw in range(1, 12)]

    for horizon in (4, 6, 8):
        ticker = build_ticker(bootstrap, fixtures, horizon)
        assert ticker.horizon == horizon
        assert ticker.start_event == 1
        assert ticker.gameweeks == list(range(1, horizon + 1))
        assert len(ticker.teams[0].cells) == horizon


def test_average_skips_blank_gameweeks() -> None:
    events = [_event(1, nxt=True), _event(2), _event(3)]
    # ARS plays GW1 (FDR 2) and GW3 (FDR 4). GW2 is blank.
    fixtures = [
        _fixture(1, 1, 2, 2, 4),
        _fixture(3, 1, 3, 4, 3),
    ]
    ticker = build_ticker(_bootstrap(events, TEAMS), fixtures, horizon=4)
    arsenal = next(row for row in ticker.teams if row.short_name == "ARS")
    assert [len(cell.fixtures) for cell in arsenal.cells] == [1, 0, 1]
    assert arsenal.average_fdr == 3.0


def test_double_contributes_two_fdrs_to_average() -> None:
    events = [_event(1, nxt=True), _event(2)]
    fixtures = [
        _fixture(1, 1, 2, 2, 4),
        _fixture(1, 1, 3, 4, 3),
    ]
    ticker = build_ticker(_bootstrap(events, TEAMS), fixtures, horizon=4)
    arsenal = next(row for row in ticker.teams if row.short_name == "ARS")
    assert len(arsenal.cells[0].fixtures) == 2
    assert arsenal.average_fdr == 3.0


def test_fdr_uses_home_or_away_side() -> None:
    events = [_event(1, nxt=True)]
    fixtures = [_fixture(1, 1, 2, 2, 5)]
    ticker = build_ticker(_bootstrap(events, TEAMS), fixtures, horizon=4)
    arsenal = next(row for row in ticker.teams if row.short_name == "ARS")
    liverpool = next(row for row in ticker.teams if row.short_name == "LIV")

    assert arsenal.cells[0].fixtures == [CellFixture(opponent_short="LIV", home=True, fdr=2)]
    assert liverpool.cells[0].fixtures[0].opponent_short == "ARS"
    assert liverpool.cells[0].fixtures[0].home is False
    assert liverpool.cells[0].fixtures[0].fdr == 5


def test_teams_sorted_easiest_average_first() -> None:
    events = [_event(1, nxt=True), _event(2)]
    fixtures = [
        _fixture(1, 1, 2, 5, 2),
        _fixture(2, 3, 1, 3, 4),
    ]
    ticker = build_ticker(_bootstrap(events, TEAMS), fixtures, horizon=4)
    names = [row.short_name for row in ticker.teams]
    averages = {row.short_name: row.average_fdr for row in ticker.teams}
    assert averages["LIV"] == 2.0
    assert averages["CHE"] == 3.0
    assert averages["ARS"] == 4.5
    assert names == ["LIV", "CHE", "ARS"]


def test_unscheduled_fixtures_are_ignored() -> None:
    events = [_event(1, nxt=True)]
    fixtures = [_fixture(None, 1, 2, 2, 4)]
    ticker = build_ticker(_bootstrap(events, TEAMS), fixtures, horizon=4)
    arsenal = next(row for row in ticker.teams if row.short_name == "ARS")
    assert arsenal.cells[0].fixtures == []
    assert arsenal.average_fdr is None


def test_real_payload_smoke() -> None:
    bootstrap = json.loads((FIXTURES_DIR / "bootstrap-static.json").read_text())
    fixtures = json.loads((FIXTURES_DIR / "fixtures.json").read_text())
    ticker = build_ticker(bootstrap, fixtures, horizon=6)
    assert ticker.start_event == 1
    assert ticker.gameweeks == [1, 2, 3, 4, 5, 6]
    assert len(ticker.teams) == 20
    assert all(len(row.cells) == 6 for row in ticker.teams)
    assert ticker.teams == sorted(
        ticker.teams,
        key=lambda row: (row.average_fdr is None, row.average_fdr or 0.0, row.short_name),
    )
