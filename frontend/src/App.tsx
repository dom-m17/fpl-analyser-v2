import { BrowserRouter, NavLink, Route, Routes } from 'react-router-dom'
import { Fixtures } from './pages/Fixtures'

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
          </nav>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<Fixtures />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
