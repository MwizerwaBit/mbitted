"""MwizerwaBit scaffolder.

Reads a resource spec and emits the matching FastAPI route, SQLAlchemy model,
Pydantic schemas, CRUD class, and Alembic migration, wired into the sample
app's conventions.

Run with::

    python -m scaffolder path/to/widget.json --app-root ../sample-app
"""

__version__ = "0.1.0"
