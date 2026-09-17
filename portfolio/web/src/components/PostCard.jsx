import { Link } from 'react-router-dom'

export default function PostCard({ post }) {
  const date = post.published_at
    ? new Date(post.published_at).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : null

  return (
    <article className="card">
      <h2 className="title">
        <Link to={`/blog/${post.slug}`} className="card-title-link">
          {post.title}
        </Link>
      </h2>
      <p className="summary">{post.summary}</p>
      {date && (
        <time className="footnote" dateTime={post.published_at}>
          {date}
        </time>
      )}
    </article>
  )
}
