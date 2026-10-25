from __future__ import annotations

from dataclasses import dataclass

ALLOWED_HORIZONS = (4, 5, 6, 7, 8)


@dataclass(frozen=True)
class CellFixture:
    opponent_short: str
    home: bool
    fdr: int


@dataclass(frozen=True)
class Cell:
    event: int
    fixtures: list[CellFixture]


@dataclass(frozen=True)
class TeamRow:
    id: int
    name: str
    short_name: str
    average_fdr: float | None
    cells: list[Cell]


@dataclass(frozen=True)
class Ticker:
    start_event: int
    horizon: int
    gameweeks: list[int]
    teams: list[TeamRow]


def start_event_id(events: list[dict]) -> int:
    for event in events:
        if event.get("is_current") and not event.get("finished"):
            return event["id"]
    for event in events:
        if event.get("is_next"):
            return event["id"]
    raise ValueError("no current or next event")


def event_window(events: list[dict], start_id: int, horizon: int) -> list[int]:
    ids = sorted(event["id"] for event in events if event["id"] >= start_id)
    return ids[:horizon]


def upcoming_gameweeks(bootstrap: dict, horizon: int) -> tuple[int, list[int]]:
    events = bootstrap["events"]
    start = start_event_id(events)
    return start, event_window(events, start, horizon)


def team_cells(
    fixtures: list[dict],
    gameweeks: list[int],
    team_id: int,
    short_by_id: dict[int, str],
) -> list[Cell]:
    return [
        Cell(event=gw, fixtures=_cell_fixtures(fixtures, gw, team_id, short_by_id))
        for gw in gameweeks
    ]


def build_ticker(bootstrap: dict, fixtures: list[dict], horizon: int) -> Ticker:
    teams = bootstrap["teams"]
    start, gameweeks = upcoming_gameweeks(bootstrap, horizon)
    short_by_id = {team["id"]: team["short_name"] for team in teams}

    rows: list[TeamRow] = []
    for team in teams:
        cells = team_cells(fixtures, gameweeks, team["id"], short_by_id)
        fdrs = [item.fdr for cell in cells for item in cell.fixtures]
        average = sum(fdrs) / len(fdrs) if fdrs else None
        rows.append(
            TeamRow(
                id=team["id"],
                name=team["name"],
                short_name=team["short_name"],
                average_fdr=round(average, 2) if average is not None else None,
                cells=cells,
            )
        )

    rows.sort(key=lambda row: (row.average_fdr is None, row.average_fdr or 0.0, row.short_name))
    return Ticker(start_event=start, horizon=horizon, gameweeks=gameweeks, teams=rows)


def _cell_fixtures(
    fixtures: list[dict],
    gw: int,
    team_id: int,
    short_by_id: dict[int, str],
) -> list[CellFixture]:
    cells: list[CellFixture] = []
    for fixture in fixtures:
        if fixture.get("event") != gw:
            continue
        if fixture["team_h"] == team_id:
            cells.append(
                CellFixture(
                    opponent_short=short_by_id[fixture["team_a"]],
                    home=True,
                    fdr=fixture["team_h_difficulty"],
                )
            )
        elif fixture["team_a"] == team_id:
            cells.append(
                CellFixture(
                    opponent_short=short_by_id[fixture["team_h"]],
                    home=False,
                    fdr=fixture["team_a_difficulty"],
                )
            )
    return cells
