import { useEffect, useState } from 'react'
import PostCard from './components/PostCard.jsx'

export default function App() {
  const [posts, setPosts] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/api/v1/posts')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(setPosts)
      .catch((err) => setError(err.message))
  }, [])

  return (
    <div className="page">
      <header className="hero">
        <h1 className="large-title">Portfolio + Blog</h1>
        <p className="subhead">End-to-end SaaS, built with FastAPI and React.</p>
      </header>

      <main className="content">
        {error && (
          <p className="footnote">
            Couldn't reach the backend: {error}. Start it with{' '}
            <code>uvicorn app.main:app --reload</code>.
          </p>
        )}
        <section className="posts" aria-label="Blog posts">
          {posts.map((post) => (
            <PostCard key={post.slug} post={post} />
          ))}
        </section>
      </main>
    </div>
  )
}
