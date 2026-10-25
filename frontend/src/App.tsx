import { BrowserRouter, NavLink, Route, Routes } from 'react-router-dom'
import { Fixtures } from './pages/Fixtures'
import { Players } from './pages/Players'

export default function App() {
  return (
    <BrowserRouter>
      <div className="shell">
        <header className="top">
          <p className="brand">FPL Analyser</p>
          <nav>
            <NavLink to="/" end>
              Fixtures
            </NavLink>
            <NavLink to="/players">Players</NavLink>
          </nav>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<Fixtures />} />
            <Route path="/players" element={<Players />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
