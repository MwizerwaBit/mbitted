import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import PostCard from '../components/PostCard.jsx'
import Reveal from '../components/Reveal.jsx'
import Skeleton from '../components/Skeleton.jsx'
import { splitTags } from '../lib/content.js'
import useSeo from '../hooks/useSeo.js'

const STACK = ['FastAPI', 'PostgreSQL', 'React', 'Flutter', 'Apple HIG']

export default function Home() {
  const [projects, setProjects] = useState(null)
  const [posts, setPosts] = useState(null)
  const [error, setError] = useState(null)

  useSeo({
    title: null,
    description:
      'Portfolio and blog of MwizerwaBit — building SaaS products end-to-end with FastAPI, Postgres, React, and Flutter.',
  })

  useEffect(() => {
    Promise.all([api.listProjects(), api.listPosts(true)])
      .then(([ps, blog]) => {
        setProjects(ps)
        setPosts(blog)
      })
      .catch((err) => setError(err.message))
  }, [])

  const featured = (projects || []).filter((p) => p.featured)
  const recent = (posts || []).slice(0, 3)

  return (
    <>
      <section className="hero">
        <div className="container">
          <p className="hero-eyebrow">Full-stack SaaS engineer</p>
          <h1 className="hero-title">
            SaaS products, built <span className="grad">end-to-end</span>.
          </h1>
          <p className="hero-sub">
            FastAPI + Postgres backends, React web apps, and Flutter mobile apps —
            designed to Apple's Human Interface Guidelines so every surface feels
            native and consistent.
          </p>
          <div className="hero-actions">
            <a className="button primary" href="#work">
              View work
            </a>
            <Link className="button" to="/blog">
              Read the blog
            </Link>
          </div>
          <div className="hero-stack">
            {STACK.map((t) => (
              <span key={t} className="tag">
                {t}
              </span>
            ))}
          </div>
        </div>
      </section>

      {error && (
        <div className="container">
          <p className="empty error">
            Couldn't reach the backend: {error}. Start it with{' '}
            <code className="inline-code">uvicorn app.main:app --reload</code>.
          </p>
        </div>
      )}

      <section className="section" id="work">
        <div className="container">
          <div className="section-head">
            <h2 className="section-title">Featured work</h2>
          </div>

          {projects === null && !error ? (
            <div className="project-grid">
              <Skeleton variant="block" />
              <Skeleton variant="block" />
              <Skeleton variant="block" />
            </div>
          ) : (
            <div className="project-grid">
              {featured.map((project, i) => (
                <Reveal key={project.slug} delay={(i % 3) * 60}>
                  <article className="project-card">
                    <div className={`project-media g${i % 4}`} aria-hidden="true">
                      {project.title.charAt(0).toUpperCase()}
                    </div>
                    <div className="project-body">
                      <h3 className="project-title">{project.title}</h3>
                      <p className="project-summary">{project.description}</p>
                      <div className="tag-row">
                        {splitTags(project.tags).map((t) => (
                          <span key={t} className="tag">
                            {t}
                          </span>
                        ))}
                      </div>
                      {project.url && (
                        <a
                          className="project-link"
                          href={project.url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          View project ↗
                        </a>
                      )}
                    </div>
                  </article>
                </Reveal>
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="section-head">
            <h2 className="section-title">Recent posts</h2>
            <Link to="/blog" className="section-link">
              All posts →
            </Link>
          </div>

          {posts === null && !error ? (
            <div className="posts">
              <Skeleton variant="card" />
              <Skeleton variant="card" />
            </div>
          ) : (
            <div className="posts">
              {recent.map((post) => (
                <PostCard key={post.slug} post={post} />
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  )
}
