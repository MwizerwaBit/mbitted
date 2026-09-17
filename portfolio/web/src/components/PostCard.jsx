import { Link } from 'react-router-dom'
import { formatDate, readTime, splitTags } from '../lib/content.js'

export default function PostCard({ post }) {
  const date = formatDate(post.published_at)
  const mins = readTime(post.body)
  const tags = splitTags(post.tags)

  return (
    <article className="post-card">
      <div className="post-meta">
        {date && (
          <>
            <time dateTime={post.published_at}>{date}</time>
            <span className="dot" aria-hidden="true">
              ·
            </span>
          </>
        )}
        <span>{mins} min read</span>
      </div>
      <h2 className="post-title">
        <Link to={`/blog/${post.slug}`}>{post.title}</Link>
      </h2>
      {post.summary && <p className="post-summary">{post.summary}</p>}
      {tags.length > 0 && (
        <div className="tag-row">
          {tags.map((t) => (
            <span key={t} className="tag">
              {t}
            </span>
          ))}
        </div>
      )}
      <div className="post-footer">
        <Link to={`/blog/${post.slug}`} className="link">
          Read →
        </Link>
      </div>
    </article>
  )
}
