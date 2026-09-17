import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import StatCard from '../components/StatCard.jsx'

const emptyForm = { slug: '', title: '', summary: '', body: '', published: true }

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [posts, setPosts] = useState([])
  const [error, setError] = useState(null)
  const [notice, setNotice] = useState(null)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)

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
      <header className="hero">
        <h1 className="large-title">Dashboard</h1>
        <p className="subhead">Content management for the blog.</p>
      </header>

      {error && <p className="footnote error">Error: {error}</p>}
      {notice && <p className="footnote notice">{notice}</p>}

      {stats && (
        <div className="stat-grid">
          <StatCard label="Total posts" value={stats.total_posts} />
          <StatCard label="Published" value={stats.published_posts} />
          <StatCard label="Drafts" value={stats.draft_posts} />
          <StatCard label="Projects" value={stats.total_projects} />
        </div>
      )}

      <section>
        <h2 className="section-title">{editing ? 'Edit post' : 'New post'}</h2>
        <form className="card form" onSubmit={submit}>
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
              <button type="button" className="button" onClick={reset}>
                Cancel
              </button>
            )}
          </div>
        </form>
      </section>

      <section>
        <h2 className="section-title">Posts</h2>
        <div className="post-list">
          {posts.map((post) => (
            <div key={post.id} className="card post-row">
              <div className="post-row-main">
                <div className="title">
                  <Link to={`/blog/${post.slug}`} className="card-title-link">
                    {post.title}
                  </Link>
                </div>
                <div className="footnote">
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
      </section>
    </>
  )
}
