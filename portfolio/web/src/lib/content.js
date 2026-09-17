// Small content helpers shared across pages: tag parsing, read time, dates.

/** Split a comma-separated tag string into trimmed, non-empty tags. */
export function splitTags(raw) {
  if (!raw) return []
  return raw
    .split(',')
    .map((t) => t.trim())
    .filter(Boolean)
}

/** Estimate reading time in minutes (average 220 wpm). */
export function readTime(body = '') {
  const words = String(body)
    .trim()
    .split(/\s+/)
    .filter(Boolean).length
  return Math.max(1, Math.round(words / 220))
}

/** Format an ISO datetime as a short, locale-aware date. */
export function formatDate(iso) {
  if (!iso) return null
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}
