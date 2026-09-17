# Sample App

A minimal **FastAPI + PostgreSQL** application with two resources — **User** and
**Project** — built as the proving ground for MwizerwaBit's scaffolder. It
exists so generated scaffolding (FastAPI routes, Postgres migrations, and the
React/Flutter UI counterparts) has a concrete, conventional target to match.

This app intentionally stays dependency-light: FastAPI, SQLAlchemy 2.0 (sync),
Alembic, psycopg2, and pydantic-settings. No async drivers, no ORM plugins, no
extra service layer.

## Stack

| Concern    | Choice                              |
| ---------- | ----------------------------------- |
| Web        | FastAPI (sync endpoints)            |
| ORM        | SQLAlchemy 2.0 typed (`Mapped`)     |
| Migrations | Alembic                             |
| Database   | PostgreSQL (via `psycopg2`)         |
| Config     | pydantic-settings (`Settings`)      |
| Server     | uvicorn                             |

## Project layout

```
sample-app/
├── app/
│   ├── main.py            # FastAPI app + router registration
│   ├── core/config.py     # Settings (single source of env config)
│   ├── db/
│   │   ├── base.py        # DeclarativeBase
│   │   └── session.py     # engine, SessionLocal, get_db dependency
│   ├── models/            # SQLAlchemy ORM models (one file per resource)
│   ├── schemas/           # Pydantic schemas (one file per resource)
│   ├── crud/              # CRUD classes (generic base + thin per-resource)
│   └── api/
│       ├── deps.py        # shared dependencies (DBSession)
│       └── routes/        # HTTP endpoints (one file per resource)
├── alembic/               # migrations + env.py
├── alembic.ini
├── requirements.txt
└── .env.example
```

## Conventions (what the scaffolder targets)

Each resource is expressed as four files that follow the same shape, so a new
resource (`Widget`) is always added the same way:

1. **Model** — `app/models/widget.py`: a `Base` subclass with `__tablename__`,
   a UUID primary key, `created_at`/`updated_at` timestamps, and any foreign
   keys/relationships.
2. **Schema** — `app/schemas/widget.py`: `WidgetCreate`, `WidgetUpdate`,
   `WidgetRead` (all derive from `ORMModel` with `from_attributes=True`).
3. **CRUD** — `app/crud/widget.py`: a thin `CRUDWidget(CRUDBase[Widget])` with
   only resource-specific lookups, exposed as a module-level `widget` instance.
4. **Router** — `app/api/routes/widget.py`: `POST`/`GET`/`GET by id`/`PATCH`/
   `DELETE` using the shared `DBSession` dependency.

Cross-cutting rules the scaffolder must preserve:

- **UUID primary keys** (`uuid.uuid4()`, client-side default — no server default).
- **Timestamps** on every table: `created_at` and `updated_at`, both
  `DateTime(timezone=True)` with `server_default=func.now()`; `updated_at` also
  has `onupdate=func.now()`.
- **Config** flows only through `app.core.config.Settings`; no module reads
  `os.environ` directly.
- **Sync SQLAlchemy** with a request-scoped session via `get_db`.
- **Versioned schema changes**: every model change gets an Alembic migration;
  new models must be imported in `app/models/__init__.py` (for autogenerate).
- **Relationship convention**: a child resource owns the FK (`owner_id` →
  `users.id`) plus a `relationship` back-reference on the parent.

## Setup

1. Create a PostgreSQL database:

   ```bash
   createdb sample_app
   ```

2. Install dependencies (in a virtualenv):

   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Configure the connection:

   ```bash
   cp .env.example .env   # then edit DATABASE_URL if needed
   ```

4. Run migrations:

   ```bash
   alembic upgrade head
   ```

5. Start the server:

   ```bash
   uvicorn app.main:app --reload
   ```

   Interactive docs at `http://localhost:8000/docs`.

## API

| Method   | Path                    | Description              |
| -------- | ----------------------- | ------------------------ |
| `GET`    | `/health`               | Liveness check           |
| `POST`   | `/api/v1/users`         | Create a user            |
| `GET`    | `/api/v1/users`         | List users               |
| `GET`    | `/api/v1/users/{id}`    | Get a user               |
| `PATCH`  | `/api/v1/users/{id}`    | Update a user            |
| `DELETE` | `/api/v1/users/{id}`    | Delete a user            |
| `POST`   | `/api/v1/projects`      | Create a project         |
| `GET`    | `/api/v1/projects`      | List projects            |
| `GET`    | `/api/v1/projects/{id}` | Get a project            |
| `PATCH`  | `/api/v1/projects/{id}` | Update a project         |
| `DELETE` | `/api/v1/projects/{id}` | Delete a project         |

### Example

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H 'Content-Type: application/json' \
  -d '{"email": "ada@example.com", "full_name": "Ada Lovelace"}'

curl -X POST http://localhost:8000/api/v1/projects \
  -H 'Content-Type: application/json' \
  -d '{"name": "Scaffolder", "description": "Codegen engine", "owner_id": "<user-id>"}'
```

## Out of scope (deliberately)

- Authentication / authorization (no auth dependency in the stack).
- Endpoint tests (`pytest` + `httpx`) — planned as a follow-up issue once this
  app is frozen as the scaffolder target.
- Nested relationships in read schemas (e.g. embedding `owner` in
  `ProjectRead`) — kept flat for the minimal proving ground; the scaffolder can
  opt in to eager-loading + nesting as a convention upgrade.
- `EmailStr` validation — email is a plain `str` to avoid the `email-validator`
  dependency; swap in `pydantic[email]` if you want strict validation.
