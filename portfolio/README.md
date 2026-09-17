# Portfolio + Blog

Personal portfolio website with a blog, built on the MwizerwaBit stack:

- **Backend** — FastAPI (`portfolio/backend/`), serving an in-memory post store
  for now. PostgreSQL + SQLAlchemy + Alembic come next, mirroring `sample-app`.
- **Web** — React + Vite (`portfolio/web/`), styled with Apple HIG spacing,
  typography, and system colors (SF Pro stack, 4pt spacing scale, light/dark).

## Run locally

### Backend

```bash
cd portfolio/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API: http://localhost:8000 — `GET /health`, `GET /api/v1/posts`, `GET /api/v1/posts/{slug}`.

### Web

```bash
cd portfolio/web
npm install
npm run dev
```

Web: http://localhost:5173 — Vite proxies `/api` to the backend on :8000.

## Roadmap

- [ ] PostgreSQL + SQLAlchemy + Alembic migrations (port `sample-app` conventions)
- [ ] Blog CRUD endpoints + markdown rendering
- [ ] Flutter app following Apple HIG
- [ ] Tests for endpoints and components
