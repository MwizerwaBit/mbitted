import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import StatCard from '../components/StatCard.jsx'
import Skeleton from '../components/Skeleton.jsx'
import useSeo from '../hooks/useSeo.js'

const emptyForm = {
  slug: '',
  title: '',
  summary: '',
  body: '',
  tags: '',
  published: true,
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [posts, setPosts] = useState([])
  const [error, setError] = useState(null)
  const [notice, setNotice] = useState(null)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)

  useSeo({ title: 'Dashboard', description: 'Content management for the blog.' })

  const load = () => {
    Promise.all([api.dashboardStats(), api.listPosts()])
      .then(([s, ps]) => {
        setStats(s)
        setPosts(ps)
      })
      .catch((err) => setError(err.message))
  }

  useEffect(load, [])

  const reset = () => {
    setEditing(null)
    setForm(emptyForm)
    setNotice(null)
  }

  const submit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      if (editing) {
        await api.updatePost(editing.id, form)
        setNotice('Post updated.')
      } else {
        await api.createPost(form)
        setNotice('Post created.')
      }
      reset()
      load()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const startEdit = (post) => {
    setEditing(post)
    setForm({
      slug: post.slug,
      title: post.title,
      summary: post.summary,
      body: post.body,
      tags: post.tags || '',
      published: post.published,
    })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const remove = async (post) => {
    if (!window.confirm(`Delete “${post.title}”?`)) return
    setError(null)
    try {
      await api.deletePost(post.id)
      setNotice('Post deleted.')
      if (editing?.id === post.id) reset()
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  const setField = (key) => (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setForm({ ...form, [key]: value })
  }

  return (
    <>
      <section className="hero">
        <div className="container">
          <p className="hero-eyebrow">Dashboard</p>
          <h1 className="hero-title">Content studio.</h1>
          <p className="hero-sub">Write, edit, and publish blog posts.</p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          {error && <p className="empty error">Error: {error}</p>}
          {notice && <p className="empty notice">{notice}</p>}

          {stats ? (
            <div className="stat-grid">
              <StatCard label="Total posts" value={stats.total_posts} />
              <StatCard label="Published" value={stats.published_posts} />
              <StatCard label="Drafts" value={stats.draft_posts} />
              <StatCard label="Projects" value={stats.total_projects} />
            </div>
          ) : !error ? (
            <Skeleton variant="lines" lines={2} />
          ) : null}

          <h2 className="section-title">{editing ? 'Edit post' : 'New post'}</h2>
          <form className="panel form" onSubmit={submit}>
            <label className="field">
              <span>Slug</span>
              <input
                value={form.slug}
                onChange={setField('slug')}
                required
                placeholder="my-post-slug"
              />
            </label>
            <label className="field">
              <span>Title</span>
              <input value={form.title} onChange={setField('title')} required />
            </label>
            <label className="field">
              <span>Summary</span>
              <input value={form.summary} onChange={setField('summary')} />
            </label>
            <label className="field">
              <span>Tags (comma-separated)</span>
              <input
                value={form.tags}
                onChange={setField('tags')}
                placeholder="FastAPI, Design"
              />
            </label>
            <label className="field">
              <span>Body (Markdown)</span>
              <textarea rows={8} value={form.body} onChange={setField('body')} />
            </label>
            <label className="field checkbox">
              <input
                type="checkbox"
                checked={form.published}
                onChange={setField('published')}
              />
              <span>Published</span>
            </label>
            <div className="form-actions">
              <button type="submit" className="button primary" disabled={saving}>
                {saving ? 'Saving…' : editing ? 'Save changes' : 'Create post'}
              </button>
              {editing && (
                <button type="button" className="button ghost" onClick={reset}>
                  Cancel
                </button>
              )}
            </div>
          </form>

          <h2 className="section-title" style={{ marginTop: 'var(--s-8)' }}>
            Posts
          </h2>
          <div className="post-list">
            {posts.map((post) => (
              <div key={post.id} className="panel post-row">
                <div className="post-row-main">
                  <div className="post-row-title">
                    <Link to={`/blog/${post.slug}`}>{post.title}</Link>
                  </div>
                  <div className="post-row-meta">
                    {post.slug}
                    {post.published ? '' : ' · draft'}
                  </div>
                </div>
                <div className="post-row-actions">
                  <button className="button small" onClick={() => startEdit(post)}>
                    Edit
                  </button>
                  <button
                    className="button small danger"
                    onClick={() => remove(post)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  )
}
