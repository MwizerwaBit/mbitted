import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api.js'
import Markdown from '../components/Markdown.jsx'

export default function BlogPost() {
  const { slug } = useParams()
  const [post, setPost] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    api
      .getPost(slug)
      .then(setPost)
      .catch((err) => setError(err.message))
  }, [slug])

  if (error) {
    return (
      <>
        <p className="footnote error">Couldn't load this post: {error}</p>
        <p>
          <Link to="/blog" className="link">
            ← Back to blog
          </Link>
        </p>
      </>
    )
  }

  if (!post) return <p className="footnote">Loading…</p>

  return (
    <article>
      <header className="hero">
        <p className="footnote">
          <Link to="/blog" className="link">
            ← Blog
          </Link>
        </p>
        <h1 className="large-title">{post.title}</h1>
        {post.published_at && (
          <time className="footnote" dateTime={post.published_at}>
            {new Date(post.published_at).toLocaleDateString(undefined, {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </time>
        )}
      </header>
      <Markdown text={post.body} />
    </article>
  )
}
