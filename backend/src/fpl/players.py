from __future__ import annotations

from dataclasses import dataclass

from fpl.ticker import Cell, team_cells, upcoming_gameweeks

PLAYER_HORIZON = 5

POSITION_SHORT = {
    "Goalkeeper": "GKP",
    "Defender": "DEF",
    "Midfielder": "MID",
    "Forward": "FWD",
}


@dataclass(frozen=True)
class PlayerRow:
    id: int
    web_name: str
    team_short: str
    position: str
    price: float | None
    fixtures: list[Cell]


@dataclass(frozen=True)
class PlayersPage:
    start_event: int
    gameweeks: list[int]
    players: list[PlayerRow]


def latest_prices(playerstats: list[dict]) -> dict[int, float]:
    """Price from each player's highest-gameweek row. playerstats has one row per player per GW."""
    latest: dict[int, tuple[int, float]] = {}
    for row in playerstats:
        player_id = int(row["id"])
        gw = int(row["gw"])
        if player_id not in latest or gw > latest[player_id][0]:
            latest[player_id] = (gw, float(row["now_cost"]))
    return {player_id: price for player_id, (_, price) in latest.items()}


def build_players(
    bootstrap: dict,
    fixtures: list[dict],
    players: list[dict],
    playerstats: list[dict],
    horizon: int = PLAYER_HORIZON,
) -> PlayersPage:
    teams = bootstrap["teams"]
    start, gameweeks = upcoming_gameweeks(bootstrap, horizon)
    short_by_id = {team["id"]: team["short_name"] for team in teams}
    team_by_code = {team["code"]: team for team in teams}
    prices = latest_prices(playerstats)

    cells_by_team = {
        team["id"]: team_cells(fixtures, gameweeks, team["id"], short_by_id) for team in teams
    }

    rows: list[PlayerRow] = []
    for player in players:
        team = team_by_code.get(int(player["team_code"]))
        if team is None:
            continue
        player_id = int(player["player_id"])
        rows.append(
            PlayerRow(
                id=player_id,
                web_name=player["web_name"],
                team_short=team["short_name"],
                position=POSITION_SHORT.get(player["position"], player["position"]),
                price=prices.get(player_id),
                fixtures=cells_by_team[team["id"]],
            )
        )

    rows.sort(key=lambda row: (row.price is None, -(row.price or 0.0), row.web_name))
    return PlayersPage(start_event=start, gameweeks=gameweeks, players=rows)
