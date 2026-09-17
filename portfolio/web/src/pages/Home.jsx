import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import PostCard from '../components/PostCard.jsx'

export default function Home() {
  const [projects, setProjects] = useState([])
  const [posts, setPosts] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([api.listProjects(), api.listPosts(true)])
      .then(([ps, blog]) => {
        setProjects(ps)
        setPosts(blog)
      })
      .catch((err) => setError(err.message))
  }, [])

  const featured = projects.filter((p) => p.featured)
  const recent = posts.slice(0, 3)

  return (
    <>
      <section className="hero">
        <h1 className="large-title">MwizerwaBit</h1>
        <p className="subhead">
          I build SaaS products end-to-end — FastAPI + Postgres backends, React
          web apps, and Flutter mobile apps — all following Apple's Human
          Interface Guidelines.
        </p>
      </section>

      {error && (
        <p className="footnote error">
          Couldn't reach the backend: {error}. Start it with{' '}
          <code>uvicorn app.main:app --reload</code>.
        </p>
      )}

      {featured.length > 0 && (
        <section>
          <h2 className="section-title">Featured work</h2>
          <div className="project-grid">
            {featured.map((project) => (
              <article key={project.slug} className="card">
                <h3 className="title">{project.title}</h3>
                <p className="summary">{project.description}</p>
                {project.tags && (
                  <p className="footnote">
                    {project.tags
                      .split(',')
                      .map((t) => t.trim())
                      .filter(Boolean)
                      .join(' · ')}
                  </p>
                )}
                {project.url && (
                  <a
                    className="link"
                    href={project.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    View project ↗
                  </a>
                )}
              </article>
            ))}
          </div>
        </section>
      )}

      {recent.length > 0 && (
        <section>
          <h2 className="section-title">Recent posts</h2>
          <div className="posts">
            {recent.map((post) => (
              <PostCard key={post.slug} post={post} />
            ))}
          </div>
          <p>
            <Link to="/blog" className="link">
              All posts →
            </Link>
          </p>
        </section>
      )}
    </>
  )
}
