export type CellFixture = {
  opponent_short: string
  home: boolean
  fdr: number
}

export type Cell = {
  event: number
  fixtures: CellFixture[]
}

export type TeamRow = {
  id: number
  name: string
  short_name: string
  average_fdr: number | null
  cells: Cell[]
}

export type Ticker = {
  start_event: number
  horizon: number
  gameweeks: number[]
  teams: TeamRow[]
}

export type Horizon = 4 | 6 | 8

export async function fetchTicker(horizon: Horizon): Promise<Ticker> {
  const response = await fetch(`/api/fixtures/ticker?horizon=${horizon}`)
  if (!response.ok) {
    const body = await response.text()
    throw new Error(body || `HTTP ${response.status}`)
  }
  return response.json() as Promise<Ticker>
}
