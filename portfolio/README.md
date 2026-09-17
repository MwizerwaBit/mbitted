# Portfolio + Blog + Dashboard

Personal portfolio website with a blog and an admin dashboard, built on the
MwizerwaBit stack (FastAPI + React, Apple HIG styling).

- **Backend** — FastAPI (`backend/`) with a real database via SQLAlchemy.
  Defaults to SQLite so it runs with zero external services; set `DATABASE_URL`
  to a Postgres DSN for production.
- **Web** — React + Vite (`web/`), styled with Apple HIG tokens (SF Pro stack,
  4pt spacing, system colors, light/dark).

## Run locally

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API: http://localhost:8000/docs

### Web

```bash
cd web
npm install
npm run dev
```

Web: http://localhost:5173 — Vite proxies `/api` to the backend on :8000.

## Features

- **Portfolio** — hero + featured projects (`/`).
- **Blog** — published posts list (`/blog`) and Markdown-rendered detail
  (`/blog/:slug`).
- **Dashboard** — stats cards + create/edit/delete posts (`/dashboard`).

## API

| Method | Path                        | Description                    |
| ------ | --------------------------- | ------------------------------ |
| GET    | `/health`                   | Liveness check                 |
| GET    | `/api/v1/posts`             | List posts (`?published=` opt) |
| POST   | `/api/v1/posts`             | Create a post                  |
| GET    | `/api/v1/posts/{slug}`      | Get one post by slug           |
| PUT    | `/api/v1/posts/{id}`        | Update a post                  |
| DELETE | `/api/v1/posts/{id}`        | Delete a post                  |
| GET    | `/api/v1/projects`          | List projects (`?featured=`)   |
| POST   | `/api/v1/projects`          | Create a project               |
| GET    | `/api/v1/dashboard/stats`   | Aggregate dashboard stats      |

## Roadmap

- [ ] Postgres + Alembic migrations (port `sample-app` conventions)
- [ ] Auth for the dashboard
- [ ] Flutter app following Apple HIG
- [ ] Tests for endpoints and components
