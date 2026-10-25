import csv
from pathlib import Path

from fpl.players import build_players, latest_prices
from fpl.ticker import CellFixture

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _rows(name: str) -> list[dict]:
    with (FIXTURES_DIR / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


PLAYERS = _rows("core_players.csv")
PLAYERSTATS = _rows("core_playerstats.csv")

BOOTSTRAP = {
    "events": [{"id": gw, "is_current": False, "is_next": gw == 1, "finished": False} for gw in range(1, 8)],
    "teams": [
        {"id": 1, "code": 3, "name": "Arsenal", "short_name": "ARS"},
        {"id": 2, "code": 14, "name": "Liverpool", "short_name": "LIV"},
        {"id": 3, "code": 8, "name": "Chelsea", "short_name": "CHE"},
    ],
}


def _fixture(event: int, home: int, away: int, home_fdr: int, away_fdr: int) -> dict:
    return {
        "event": event,
        "team_h": home,
        "team_a": away,
        "team_h_difficulty": home_fdr,
        "team_a_difficulty": away_fdr,
    }


FIXTURES = [
    _fixture(1, 1, 2, 4, 4),
    _fixture(2, 3, 1, 3, 2),
    _fixture(3, 2, 3, 2, 5),
    _fixture(4, 1, 3, 3, 3),
    _fixture(4, 2, 1, 4, 4),
    # GW5 is a blank for everyone.
    _fixture(6, 1, 2, 4, 4),
]


def test_latest_prices_takes_the_highest_gameweek_row() -> None:
    assert latest_prices(PLAYERSTATS) == {1: 10.2, 2: 14.4, 3: 4.9, 4: 6.0}


def test_players_are_sorted_by_price_descending_with_unpriced_last() -> None:
    page = build_players(BOOTSTRAP, FIXTURES, PLAYERS, PLAYERSTATS, horizon=5)
    assert [p.web_name for p in page.players] == ["M.Salah", "Saka", "Sánchez", "Newbie"]
    assert page.players[-1].price is None


def test_players_with_unknown_team_are_skipped() -> None:
    page = build_players(BOOTSTRAP, FIXTURES, PLAYERS, PLAYERSTATS, horizon=5)
    assert "Lost" not in [p.web_name for p in page.players]


def test_player_row_carries_team_and_short_position() -> None:
    page = build_players(BOOTSTRAP, FIXTURES, PLAYERS, PLAYERSTATS, horizon=5)
    sanchez = next(p for p in page.players if p.id == 3)
    assert sanchez.team_short == "CHE"
    assert sanchez.position == "GKP"


def test_player_gets_their_teams_next_fixtures() -> None:
    page = build_players(BOOTSTRAP, FIXTURES, PLAYERS, PLAYERSTATS, horizon=5)
    saka = next(p for p in page.players if p.id == 1)
    assert page.gameweeks == [1, 2, 3, 4, 5]
    assert [cell.event for cell in saka.fixtures] == [1, 2, 3, 4, 5]
    assert saka.fixtures[0].fixtures == [CellFixture(opponent_short="LIV", home=True, fdr=4)]
    assert saka.fixtures[1].fixtures == [CellFixture(opponent_short="CHE", home=False, fdr=2)]
    assert saka.fixtures[2].fixtures == []
    assert len(saka.fixtures[3].fixtures) == 2
    assert saka.fixtures[4].fixtures == []
