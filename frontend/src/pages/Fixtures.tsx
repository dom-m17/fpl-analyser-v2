import { useEffect, useMemo, useState } from 'react'
import { fetchTicker, type Cell, type Horizon, type TeamRow, type Ticker } from '../api'

type SortKey = 'team' | 'average' | `gw:${number}`
type SortDir = 'asc' | 'desc'

const HORIZONS: Horizon[] = [4, 6, 8]

export function Fixtures() {
  const [horizon, setHorizon] = useState<Horizon>(6)
  const [ticker, setTicker] = useState<Ticker | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [sortKey, setSortKey] = useState<SortKey>('average')
  const [sortDir, setSortDir] = useState<SortDir>('asc')

  useEffect(() => {
    let cancelled = false
    setError(null)
    fetchTicker(horizon)
      .then((data) => {
        if (!cancelled) {
          setTicker(data)
          setSortKey('average')
          setSortDir('asc')
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setTicker(null)
          setError(err instanceof Error ? err.message : 'failed to load ticker')
        }
      })
    return () => {
      cancelled = true
    }
  }, [horizon])

  const teams = useMemo(() => {
    if (!ticker) return []
    return sortTeams(ticker.teams, sortKey, sortDir)
  }, [ticker, sortKey, sortDir])

  function onSort(key: SortKey) {
    if (key === sortKey) {
      setSortDir((dir) => (dir === 'asc' ? 'desc' : 'asc'))
      return
    }
    setSortKey(key)
    setSortDir('asc')
  }

  return (
    <section className="page">
      <div className="toolbar">
        <h2>Fixtures</h2>
        <div className="horizons" role="group" aria-label="Horizon">
          {HORIZONS.map((n) => (
            <button
              key={n}
              type="button"
              className={n === horizon ? 'active' : ''}
              onClick={() => setHorizon(n)}
            >
              {n} GWs
            </button>
          ))}
        </div>
      </div>

      {error && <p className="status error">{error}</p>}
      {!error && !ticker && <p className="status">Loading…</p>}

      {ticker && (
        <div className="table-wrap">
          <table className="ticker">
            <thead>
              <tr>
                <th>
                  <button type="button" onClick={() => onSort('team')}>
                    Team{mark(sortKey, sortDir, 'team')}
                  </button>
                </th>
                {ticker.gameweeks.map((gw) => (
                  <th key={gw}>
                    <button type="button" onClick={() => onSort(`gw:${gw}`)}>
                      GW{gw}{mark(sortKey, sortDir, `gw:${gw}`)}
                    </button>
                  </th>
                ))}
                <th>
                  <button type="button" onClick={() => onSort('average')}>
                    Avg{mark(sortKey, sortDir, 'average')}
                  </button>
                </th>
              </tr>
            </thead>
            <tbody>
              {teams.map((team) => (
                <tr key={team.id}>
                  <td className="team">
                    <span className="short">{team.short_name}</span>
                    <span className="name">{team.name}</span>
                  </td>
                  {team.cells.map((cell) => (
                    <td key={cell.event}>
                      <CellView cell={cell} />
                    </td>
                  ))}
                  <td className="avg">
                    {team.average_fdr == null ? '–' : team.average_fdr.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="legend">
        Official FPL difficulty, 1 easiest to 5 hardest. Blanks are empty and skipped in the
        average. A double shows two fixtures in one cell.
      </p>
    </section>
  )
}

function CellView({ cell }: { cell: Cell }) {
  if (cell.fixtures.length === 0) {
    return <span className="blank">–</span>
  }
  return (
    <div className="cell-stack">
      {cell.fixtures.map((fx, i) => (
        <span key={`${fx.opponent_short}-${i}`} className={`fdr fdr-${fx.fdr}`}>
          <span className="fdr-num">{fx.fdr}</span>
          <span>
            {fx.opponent_short} ({fx.home ? 'H' : 'A'})
          </span>
        </span>
      ))}
    </div>
  )
}

function mark(current: SortKey, dir: SortDir, key: SortKey): string {
  if (current !== key) return ''
  return dir === 'asc' ? ' ↑' : ' ↓'
}

function cellScore(cell: Cell): number | null {
  if (cell.fixtures.length === 0) return null
  return cell.fixtures.reduce((sum, fx) => sum + fx.fdr, 0) / cell.fixtures.length
}

function sortTeams(teams: TeamRow[], key: SortKey, dir: SortDir): TeamRow[] {
  const copy = [...teams]
  const sign = dir === 'asc' ? 1 : -1
  copy.sort((a, b) => {
    const av = value(a, key)
    const bv = value(b, key)
    if (av == null && bv == null) return a.short_name.localeCompare(b.short_name)
    if (av == null) return 1
    if (bv == null) return -1
    if (av < bv) return -1 * sign
    if (av > bv) return 1 * sign
    return a.short_name.localeCompare(b.short_name)
  })
  return copy
}

function value(team: TeamRow, key: SortKey): string | number | null {
  if (key === 'team') return team.short_name
  if (key === 'average') return team.average_fdr
  const gw = Number(key.slice(3))
  const cell = team.cells.find((item) => item.event === gw)
  return cell ? cellScore(cell) : null
}
