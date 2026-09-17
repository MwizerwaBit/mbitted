import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api.js'
import Markdown from '../components/Markdown.jsx'
import Skeleton from '../components/Skeleton.jsx'
import { formatDate, readTime, splitTags } from '../lib/content.js'
import useSeo from '../hooks/useSeo.js'

function loadBookmarks() {
  try {
    return JSON.parse(localStorage.getItem('bookmarks') || '[]')
  } catch {
    return []
  }
}

export default function BlogPost() {
  const { slug } = useParams()
  const [post, setPost] = useState(null)
  const [error, setError] = useState(null)
  const [bookmarked, setBookmarked] = useState(() => loadBookmarks().includes(slug))
  const [copied, setCopied] = useState(false)

  useSeo({
    title: post?.title,
    description: post?.summary || undefined,
  })

  useEffect(() => {
    api
      .getPost(slug)
      .then(setPost)
      .catch((err) => setError(err.message))
  }, [slug])

  const toggleBookmark = () => {
    setBookmarked((prev) => {
      const next = !prev
      try {
        const list = loadBookmarks()
        const updated = next
          ? Array.from(new Set([...list, slug]))
          : list.filter((s) => s !== slug)
        localStorage.setItem('bookmarks', JSON.stringify(updated))
      } catch {
        // storage unavailable — bookmark still toggles for this session
      }
      return next
    })
  }

  const share = async () => {
    try {
      if (navigator.share) {
        await navigator.share({ title: post.title, url: window.location.href })
      } else {
        await navigator.clipboard.writeText(window.location.href)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      }
    } catch {
      // user cancelled the share sheet — ignore
    }
  }

  if (error) {
    return (
      <div className="container section">
        <p className="empty error">Couldn't load this post: {error}</p>
        <Link to="/blog" className="section-link">
          ← Back to blog
        </Link>
      </div>
    )
  }

  if (!post) {
    return (
      <div className="container article" aria-busy="true">
        <span className="skeleton skeleton-title" aria-hidden="true" />
        <div style={{ height: 16 }} />
        <Skeleton variant="lines" lines={6} />
      </div>
    )
  }

  const tags = splitTags(post.tags)
  const mins = readTime(post.body)

  return (
    <article className="article">
      <div className="container">
        <header className="article-head">
          <Link to="/blog" className="article-back">
            ← Back to blog
          </Link>
          <h1 className="article-title">{post.title}</h1>
          <div className="article-meta">
            {post.published_at && (
              <time dateTime={post.published_at}>{formatDate(post.published_at)}</time>
            )}
            <span aria-hidden="true">·</span>
            <span>{mins} min read</span>
          </div>
          {tags.length > 0 && (
            <div className="tag-row" style={{ marginTop: 'var(--s-4)' }}>
              {tags.map((t) => (
                <span key={t} className="tag">
                  {t}
                </span>
              ))}
            </div>
          )}
          <div className="article-actions">
            <button className="button small" onClick={share}>
              Share
            </button>
            <button
              className="button small"
              onClick={toggleBookmark}
              aria-pressed={bookmarked}
            >
              {bookmarked ? '★ Bookmarked' : '☆ Bookmark'}
            </button>
            {copied && <span className="notice">Link copied</span>}
          </div>
        </header>
        <div className="article-body">
          <Markdown text={post.body} />
        </div>
      </div>
    </article>
  )
}
