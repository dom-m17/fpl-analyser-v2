import { useEffect, useMemo, useState } from 'react'
import { fetchPlayers, type Cell, type PlayersPage } from '../api'

type PositionFilter = 'ALL' | 'GKP' | 'DEF' | 'MID' | 'FWD'

const POSITIONS: PositionFilter[] = ['ALL', 'GKP', 'DEF', 'MID', 'FWD']
const pageSize = 20

export function Players() {
  const [page, setPage] = useState<PlayersPage | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [position, setPosition] = useState<PositionFilter>('ALL')
  const [currentPage, setCurrentPage] = useState(0)

  useEffect(() => {
    let cancelled = false
    fetchPlayers()
      .then((data) => {
        if (!cancelled) setPage(data)
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'failed to load players')
      })
    return () => {
      cancelled = true
    }
  }, [])

  const players = useMemo(() => {
    if (!page) return []
    const query = search.trim().toLowerCase()
    return page.players.filter(
      (player) =>
        (position === 'ALL' || player.position === position) &&
        player.web_name.toLowerCase().includes(query),
    )
  }, [page, search, position])

  const pageCount = Math.max(1, Math.ceil(players.length / pageSize))
  const start = currentPage * pageSize
  const visiblePlayers = players.slice(start, start + pageSize)

  return (
    <section className="page">
      <div className="toolbar">
        <h2>Players</h2>
        <div className="filters">
          <input
            type="search"
            className="search"
            placeholder="Search players"
            aria-label="Search players"
            value={search}
            onChange={(event) => {
              setSearch(event.target.value)
              setCurrentPage(0)
            }}
          />
          <div className="horizons" role="group" aria-label="Position">
            {POSITIONS.map((pos) => (
              <button
                key={pos}
                type="button"
                className={pos === position ? 'active' : ''}
                onClick={() => {
                  setPosition(pos)
                  setCurrentPage(0)
                }}
              >
                {pos === 'ALL' ? 'All' : pos}
              </button>
            ))}
          </div>
        </div>
      </div>

      {error && <p className="status error">{error}</p>}
      {!error && !page && <p className="status">Loading…</p>}

      {page && (
        <>
          <div className="table-wrap">
            <table className="ticker players">
              <thead>
                <tr>
                  <th>Player</th>
                  <th>Price</th>
                  {page.gameweeks.map((gw) => (
                    <th key={gw}>GW{gw}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {visiblePlayers.map((player) => (
                  <tr key={player.id}>
                    <td className="team">
                      <span className="short">{player.web_name}</span>
                      <span className="name">
                        {player.team_short} · {player.position}
                      </span>
                    </td>
                    <td className="avg">
                      {player.price == null ? '–' : `£${player.price.toFixed(1)}m`}
                    </td>
                    {player.fixtures.map((cell) => (
                      <td key={cell.event}>
                        <FixtureBadges cell={cell} />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {players.length === 0 && <p className="status">No players match.</p>}
          </div>
          <div
            className="flex justify-between items-center mt-4"
          >
            <span>{players.length} players</span>
            <div className='flex items-center gap-3'>
              <button 
                type="button" 
                onClick={() => {setCurrentPage(currentPage-1)}}
                disabled={currentPage === 0}
                className="disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Prev
              </button>
              <span>Page {currentPage+1} of {pageCount}</span>
              <button 
                type="button" 
                onClick={() => {setCurrentPage(currentPage+1)}}
                disabled={currentPage === pageCount-1}
                className="disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}

      <p className="legend">
        Official FPL difficulty, 1 easiest to 5 hardest. Player data from FPL-Core-Insights.
      </p>
    </section>
  )
}

function FixtureBadges({ cell }: { cell: Cell }) {
  if (cell.fixtures.length === 0) {
    return <span className="blank">–</span>
  }
  return (
    <div className="cell-stack">
      {cell.fixtures.map((fx, i) => (
        <span
          key={`${fx.opponent_short}-${i}`}
          className={`fdr fdr-${fx.fdr}`}
          title={`${fx.opponent_short} (${fx.home ? 'H' : 'A'}), difficulty ${fx.fdr}`}
        >
          {fx.home ? fx.opponent_short.toLowerCase() + "(H)" : fx.opponent_short.toLowerCase() + "(A)"}
        </span>
      ))}
    </div>
  )
}
