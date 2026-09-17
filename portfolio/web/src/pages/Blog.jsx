import { useEffect, useState } from 'react'
import { api } from '../api.js'
import PostCard from '../components/PostCard.jsx'

export default function Blog() {
  const [posts, setPosts] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    api
      .listPosts(true)
      .then(setPosts)
      .catch((err) => setError(err.message))
  }, [])

  return (
    <>
      <header className="hero">
        <h1 className="large-title">Blog</h1>
        <p className="subhead">Thoughts on building SaaS products.</p>
      </header>

      {error && <p className="footnote error">Couldn't reach the backend: {error}</p>}

      <div className="posts">
        {posts.map((post) => (
          <PostCard key={post.slug} post={post} />
        ))}
      </div>

      {posts.length === 0 && !error && (
        <p className="footnote">No posts published yet.</p>
      )}
    </>
  )
}
