/**
 * Lightweight skeleton loaders that hold layout shape while data loads,
 * preventing cumulative layout shift (CLS). All variants are aria-hidden.
 */
export default function Skeleton({ variant = 'lines', lines = 3 }) {
  if (variant === 'card') {
    return (
      <div className="skeleton-card" aria-hidden="true">
        <span className="skeleton skeleton-title" />
        <span className="skeleton skeleton-line" />
        <span className="skeleton skeleton-line short" />
      </div>
    )
  }

  if (variant === 'block') {
    return <span className="skeleton skeleton-block" aria-hidden="true" />
  }

  return (
    <div className="skeleton-lines" aria-hidden="true">
      {Array.from({ length: lines }).map((_, i) => (
        <span
          key={i}
          className={`skeleton skeleton-line${i === lines - 1 ? ' short' : ''}`}
        />
      ))}
    </div>
  )
}
