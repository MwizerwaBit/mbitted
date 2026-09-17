# Scaffolder

A minimal, dependency-light (stdlib-only) CLI that turns a resource spec into
the full set of FastAPI + SQLAlchemy + Alembic files the sample app expects:

- `app/models/{resource}.py` — SQLAlchemy model (UUID PK, timestamps, FKs)
- `app/schemas/{resource}.py` — `Create` / `Update` / `Read` Pydantic schemas
- `app/crud/{resource}.py` — thin `CRUDBase` subclass (+ `get_by_*` for unique fields)
- `app/api/routes/{resource}.py` — full CRUD endpoints
- `alembic/versions/{rev}_create_{table}.py` — migration

…and wires the new resource into `models/__init__.py`, `schemas/__init__.py`,
`crud/__init__.py`, `routes/__init__.py`, and `main.py`, so it is importable and
routed with no manual edits.

## Usage

```bash
python -m scaffolder widget.json --app-root ../sample-app
```

`--app-root` defaults to `../sample-app` relative to this package. Add
`--dry-run` to print the files instead of writing them.

## Spec format

```json
{
  "name": "widget",
  "fields": [
    {"name": "name", "type": "str", "required": true, "max_length": 255, "unique": true},
    {"name": "description", "type": "text"},
    {"name": "owner_id", "type": "uuid", "required": true, "fk": "users.id", "index": true}
  ]
}
```

- `name` — singular snake_case resource name (the table defaults to its plural;
  override with `"table"`).
- `fields[].type` — `str` | `text` | `int` | `float` | `bool` | `datetime` | `uuid`.
- `required` — column is `NOT NULL` and, for strings, gets `min_length=1`.
- `max_length` — for `str` columns (default 255).
- `unique` — unique constraint + `get_by_<field>` CRUD lookup + 409 on create.
- `fk` — `"<table>.<column>"` foreign key (`ON DELETE CASCADE`), auto-indexed,
  validated in the route, and exposed as a forward `relationship()`.
- `index` — create a secondary index on the column.

## Conventions preserved

- UUID primary keys (`uuid.uuid4()`, client-side default).
- `created_at` / `updated_at` on every table (`server_default=now()`,
  `onupdate=now()` on `updated_at`).
- Sync SQLAlchemy, request-scoped `DBSession` dependency.
- Config flows only through `app.core.config.Settings` (the scaffolder touches
  no config — `env.py` already reads the same source of truth).
- A required `bool` field gets `server_default=true()` (like `is_active`), so it
  is omitted from `Create` and surfaced in `Update`/`Read` only.

## Deliberate simplifications

- Optional `str` fields carry `max_length` but not `min_length` in schemas.
- A single forward `relationship()` is emitted only for the common single-FK
  child case; the matching `back_populates` on the parent is left to you.
- FK validation detail is a generic `"{Parent} not found."` rather than the
  bespoke `"Owner user not found."` wording in the sample.
