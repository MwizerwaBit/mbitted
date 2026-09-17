// Thin fetch wrapper over the FastAPI backend. Vite proxies `/api` to :8000.

const BASE = '/api/v1'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (res.status === 204) return null
  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch {
      // non-JSON error body — keep the status message
    }
    throw new Error(detail)
  }
  return res.json()
}

export const api = {
  listPosts: (published) =>
    request(`/posts${published === undefined ? '' : `?published=${published}`}`),
  getPost: (slug) => request(`/posts/${slug}`),
  createPost: (post) => request('/posts', { method: 'POST', body: JSON.stringify(post) }),
  updatePost: (id, post) =>
    request(`/posts/${id}`, { method: 'PUT', body: JSON.stringify(post) }),
  deletePost: (id) => request(`/posts/${id}`, { method: 'DELETE' }),
  listProjects: () => request('/projects'),
  dashboardStats: () => request('/dashboard/stats'),
}
