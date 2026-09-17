import { Link } from 'react-router-dom'
import useSeo from '../hooks/useSeo.js'

export default function NotFound() {
  useSeo({
    title: 'Not found',
    description: 'This page could not be found.',
  })

  return (
    <section className="hero">
      <div className="container">
        <p className="hero-eyebrow">404</p>
        <h1 className="hero-title">404 — page not found</h1>
        <p className="hero-sub">
          The page you're looking for doesn't exist or may have moved.
        </p>
        <div className="hero-actions">
          <Link className="button primary" to="/">
            Back home
          </Link>
        </div>
      </div>
    </section>
  )
}
