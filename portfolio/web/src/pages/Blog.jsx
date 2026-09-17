import { useEffect, useMemo, useState } from 'react'
import { api } from '../api.js'
import PostCard from '../components/PostCard.jsx'
import Reveal from '../components/Reveal.jsx'
import Skeleton from '../components/Skeleton.jsx'
import { splitTags } from '../lib/content.js'
import useSeo from '../hooks/useSeo.js'

export default function Blog() {
  const [posts, setPosts] = useState(null)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('')
  const [tag, setTag] = useState('All')

  useSeo({
    title: 'Blog',
    description: 'Notes on building SaaS products — FastAPI, Postgres, React, Flutter, and design.',
  })

  useEffect(() => {
    api
      .listPosts(true)
      .then(setPosts)
      .catch((err) => setError(err.message))
  }, [])

  const allTags = useMemo(() => {
    const set = new Set()
    ;(posts || []).forEach((p) => splitTags(p.tags).forEach((t) => set.add(t)))
    return ['All', ...Array.from(set)]
  }, [posts])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return (posts || []).filter((p) => {
      const tags = splitTags(p.tags)
      const matchesTag = tag === 'All' || tags.includes(tag)
      const haystack = [p.title, p.summary, ...tags].join(' ').toLowerCase()
      return matchesTag && (!q || haystack.includes(q))
    })
  }, [posts, query, tag])

  return (
    <>
      <section className="hero">
        <div className="container">
          <p className="hero-eyebrow">Blog</p>
          <h1 className="hero-title">Writing on building SaaS.</h1>
          <p className="hero-sub">
            Notes on FastAPI, Postgres, React, Flutter, and design.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="blog-toolbar">
            <input
              className="search-input"
              type="search"
              placeholder="Search posts…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label="Search posts"
            />
            {allTags.length > 1 && (
              <div className="tag-filter" role="group" aria-label="Filter by tag">
                {allTags.map((t) => (
                  <button
                    key={t}
                    className={`filter-chip${tag === t ? ' active' : ''}`}
                    onClick={() => setTag(t)}
                    aria-pressed={tag === t}
                  >
                    {t}
                  </button>
                ))}
              </div>
            )}
          </div>

          {error && <p className="empty error">Couldn't reach the backend: {error}</p>}

          {posts === null && !error ? (
            <div className="posts">
              <Skeleton variant="card" />
              <Skeleton variant="card" />
              <Skeleton variant="card" />
            </div>
          ) : filtered.length === 0 ? (
            <p className="empty">No posts match your search.</p>
          ) : (
            <div className="posts">
              {filtered.map((post, i) => (
                <Reveal key={post.slug} delay={Math.min(i, 5) * 50}>
                  <PostCard post={post} />
                </Reveal>
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  )
}
