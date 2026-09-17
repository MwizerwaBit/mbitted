import { useEffect, useRef, useState } from 'react'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import ThemeToggle from './ThemeToggle.jsx'

const LINKS = [
  { to: '/', label: 'Portfolio', end: true },
  { to: '/blog', label: 'Blog', end: false },
  { to: '/dashboard', label: 'Dashboard', end: false },
]

const navClass = ({ isActive }) => `nav-link${isActive ? ' active' : ''}`

export default function Layout() {
  const [open, setOpen] = useState(false)
  const location = useLocation()
  const drawerRef = useRef(null)

  // Keep the off-screen drawer out of the tab order while closed.
  useEffect(() => {
    if (drawerRef.current) drawerRef.current.inert = !open
  }, [open])

  // Close the drawer and jump to the top on every route change.
  useEffect(() => {
    setOpen(false)
    window.scrollTo({ top: 0, behavior: 'instant' })
  }, [location.pathname])

  // Escape closes the drawer; body scroll is locked while it's open.
  useEffect(() => {
    if (!open) return
    const onKey = (e) => {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = ''
    }
  }, [open])

  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>

      <header className="app-header">
        <div className="container header-inner">
          <Link to="/" className="brand" aria-label="MwizerwaBit home">
            <span className="brand-mark" aria-hidden="true">
              M
            </span>
            <span>MwizerwaBit</span>
          </Link>

          <nav className="nav-desktop" aria-label="Primary">
            {LINKS.map((l) => (
              <NavLink key={l.to} to={l.to} end={l.end} className={navClass}>
                {l.label}
              </NavLink>
            ))}
          </nav>

          <div className="header-actions">
            <ThemeToggle />
            <button
              className="nav-toggle"
              aria-expanded={open}
              aria-controls="mobile-nav"
              aria-label={open ? 'Close menu' : 'Open menu'}
              onClick={() => setOpen((v) => !v)}
            >
              <span className="bar" />
              <span className="bar" />
              <span className="bar" />
            </button>
          </div>
        </div>
      </header>

      <div
        className={`nav-overlay${open ? ' open' : ''}`}
        onClick={() => setOpen(false)}
        aria-hidden="true"
      />

      <aside
        ref={drawerRef}
        id="mobile-nav"
        className={`nav-drawer${open ? ' open' : ''}`}
        aria-label="Mobile navigation"
      >
        <div className="nav-drawer-head">
          <span className="brand">
            <span className="brand-mark" aria-hidden="true">
              M
            </span>
            <span>MwizerwaBit</span>
          </span>
          <button
            className="nav-toggle"
            aria-expanded="true"
            aria-label="Close menu"
            onClick={() => setOpen(false)}
          >
            <span className="bar" />
            <span className="bar" />
            <span className="bar" />
          </button>
        </div>
        <nav className="nav-drawer-nav" aria-label="Mobile primary">
          {LINKS.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.end}
              className={navClass}
              onClick={() => setOpen(false)}
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <main id="main" className="route" key={location.pathname}>
        <Outlet />
      </main>
    </>
  )
}
