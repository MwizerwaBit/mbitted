# mbitted — MwizerwaBit's full-stack SaaS scaffolding engine

## What we're building

**mbitted** is the internal product behind MwizerwaBit. It's a code-generation
engine that turns a small, declarative spec into the complete, convention-consistent
stack for a new SaaS resource — so a feature ships in minutes instead of days of
copy-paste boilerplate.

Given a resource like `widget`, it generates:

| Layer        | Output                                                                 |
| ------------ | ---------------------------------------------------------------------- |
| Backend      | FastAPI routes, SQLAlchemy models, Pydantic schemas, CRUD classes      |
| Database     | PostgreSQL migration (Alembic) with UUID PKs, timestamps, FKs, indexes |
| Web UI       | React components following Apple HIG spacing/typography *(roadmap)*     |
| Mobile UI    | Flutter screens for iOS + Android following Apple HIG *(roadmap)*       |
| Tests        | Endpoint + model tests for existing and generated code *(roadmap)*      |

## The problem

MwizerwaBit builds SaaS products end-to-end — FastAPI + PostgreSQL backends, React
web frontends, and Flutter mobile apps. As a small team without a dedicated designer
or dedicated QA, the same pain recurs on every feature:

1. **Repetitive boilerplate** — every new endpoint means hand-writing a model, a
   schema, CRUD, a route, and a migration that are ~90% identical to the last one.
2. **Design drift** — keeping web and mobile visually consistent with Apple's
   Human Interface Guidelines is manual and error-prone without a designer.
3. **No test / review safety net** — no dedicated code review, testing, or QA, so
   regressions slip through on endpoints that were already working.

mbitted automates (1), encodes HIG conventions so (2) happens by default, and
generates the tests that close (3).

## First priority

Automate scaffolding **new FastAPI routes with matching Postgres models/migrations**,
generate **React and Flutter UI components that follow Apple HIG spacing/typography
conventions**, and **write tests for existing endpoints**. The backend scaffolder is
the first deliverable; UI generation and test generation build on the same spec.

## Current state

Two components exist today:

### `scaffolder/`

A minimal, **dependency-light (stdlib-only)** CLI. Feed it a resource spec and it
emits the full backend slice — and wires it in with no manual edits:

- `app/models/{resource}.py` — SQLAlchemy model (UUID PK, timestamps, FKs)
- `app/schemas/{resource}.py` — `Create` / `Update` / `Read` Pydantic schemas
- `app/crud/{resource}.py` — thin `CRUDBase` subclass with resource-specific lookups
- `app/api/routes/{resource}.py` — full CRUD endpoints
- `alembic/versions/{rev}_create_{table}.py` — migration

Usage:

```bash
python -m scaffolder widget.json --app-root ../sample-app
```

### `sample-app/`

A minimal **FastAPI + PostgreSQL** app with two resources — **User** and **Project** —
that acts as the proving ground the scaffolder targets. It deliberately stays
dependency-light (FastAPI, SQLAlchemy 2.0 sync, Alembic, psycopg2, pydantic-settings)
and defines the conventions every generated file must preserve.

## Stack

| Concern    | Choice                                       |
| ---------- | -------------------------------------------- |
| Backend    | FastAPI (sync), SQLAlchemy 2.0 typed (`Mapped`) |
| Migrations | Alembic                                      |
| Database   | PostgreSQL                                   |
| Config     | pydantic-settings                            |
| Scaffolder | Python stdlib only (no runtime deps)         |
| Web UI     | React *(roadmap)*                            |
| Mobile     | Flutter (iOS + Android) *(roadmap)*          |

## Conventions (the contract the scaffolder enforces)

- **UUID primary keys** — `uuid.uuid4()`, client-side default.
- **Timestamps on every table** — `created_at` / `updated_at`,
  `DateTime(timezone=True)` with `server_default=func.now()`.
- **Config in one place** — everything flows through `app.core.config.Settings`.
- **Sync SQLAlchemy** with a request-scoped session via `get_db`.
- **Versioned schema changes** — every model change gets an Alembic migration.
- **One file per resource** across models / schemas / crud / routes.
- **Apple HIG first** — web and mobile UI share one spacing/typography system so the
  generated components look native and consistent across platforms.

## Roadmap

1. ✅ **Backend scaffolder** — spec → FastAPI model/schema/CRUD/route/migration.
2. ⬜ **Endpoint tests** — generate `pytest` + `httpx` coverage for generated and
   existing endpoints.
3. ⬜ **React UI generation** — spec → HIG-compliant React components (forms, lists,
   detail views).
4. ⬜ **Flutter UI generation** — spec → HIG-compliant Flutter screens for iOS/Android.
5. ⬜ **End-to-end feature workflow** — one spec produces backend + web + mobile + tests
   in a single pass.

## Out of scope (for now)

- Authentication / authorization in the sample app.
- Nested relationships in read schemas (kept flat for the minimal proving ground).
- Strict email validation (avoiding the `email-validator` dependency).
