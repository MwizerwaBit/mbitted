import { Link, NavLink, Outlet } from 'react-router-dom'

const navLink = ({ isActive }) => `nav-link${isActive ? ' active' : ''}`

export default function Layout() {
  return (
    <div className="page">
      <header className="site-header">
        <Link to="/" className="brand">
          MwizerwaBit
        </Link>
        <nav className="nav">
          <NavLink to="/" end className={navLink}>
            Portfolio
          </NavLink>
          <NavLink to="/blog" className={navLink}>
            Blog
          </NavLink>
          <NavLink to="/dashboard" className={navLink}>
            Dashboard
          </NavLink>
        </nav>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}
