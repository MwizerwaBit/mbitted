"""In-memory post repository.

Stand-in for PostgreSQL + SQLAlchemy (next milestone). The API reads from this
store so the frontend has real data to render before the database lands.
"""

from datetime import datetime, timezone

from app.schemas import Post

# Seed data — replace with rows from Postgres once Alembic migrations land.
_POSTS: list[Post] = [
    Post(
        slug="hello",
        title="Hello, world",
        summary="The first post on this blog.",
        body="Welcome to my portfolio and blog, built with FastAPI and React.",
        published_at=datetime(2026, 9, 17, tzinfo=timezone.utc),
    ),
    Post(
        slug="about",
        title="About me",
        summary="Who I am and what I build.",
        body="I build SaaS products end-to-end with FastAPI, React, and Flutter.",
        published_at=datetime(2026, 9, 10, tzinfo=timezone.utc),
    ),
]


def list_posts() -> list[Post]:
    """Return posts, newest first."""
    return sorted(_POSTS, key=lambda p: p.published_at, reverse=True)


def get_post(slug: str) -> Post | None:
    """Return a single post by slug, or ``None`` if not found."""
    return next((p for p in _POSTS if p.slug == slug), None)
