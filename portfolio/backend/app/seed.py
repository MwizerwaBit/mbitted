"""Seed the database with starter content on first run (idempotent)."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Post, Project


def _ago(days: int) -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)


_HELLO_BODY = """Welcome to my portfolio and blog, built with **FastAPI**, **React**,
and an eye for Apple's Human Interface Guidelines.

This is a living site — the blog posts are stored in a real database, and the
dashboard lets me write, edit, and publish posts without touching code.
"""

_ABOUT_BODY = """I build SaaS products end-to-end:

- **FastAPI + PostgreSQL** backends with Alembic migrations
- **React** web frontends
- **Flutter** mobile apps for iOS and Android

Everything follows Apple HIG so it feels native and consistent across platforms.
"""

_MARKDOWN_BODY = """## Why Markdown?

Posts are stored as plain Markdown and rendered in the browser. That keeps the
content portable and review-friendly in git.

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

You can write headings, lists, code blocks, and links — everything you need for
a blog without a heavyweight CMS.
"""


def _seed_posts() -> list[Post]:
    return [
        Post(
            slug="hello-world",
            title="Hello, world",
            summary="The first post on this blog.",
            body=_HELLO_BODY,
            tags="Meta",
            published=True,
            published_at=_ago(1),
        ),
        Post(
            slug="about-me",
            title="About me",
            summary="Who I am and what I build.",
            body=_ABOUT_BODY,
            tags="Meta",
            published=True,
            published_at=_ago(6),
        ),
        Post(
            slug="markdown-in-the-blog",
            title="Writing posts in Markdown",
            summary="How the blog stores and renders content.",
            body=_MARKDOWN_BODY,
            tags="Engineering, Markdown",
            published=True,
            published_at=_ago(12),
        ),
        Post(
            slug="a-draft-post",
            title="A draft post",
            summary="This one is not published yet.",
            body="This post is a draft, so it only shows up in the dashboard.",
            tags="Draft",
            published=False,
            published_at=None,
        ),
    ]


def _seed_projects() -> list[Project]:
    return [
        Project(
            slug="mbitted",
            title="mbitted scaffolding engine",
            description=(
                "Generates FastAPI routes, Postgres models, React components, and "
                "Flutter screens from a single spec — killing boilerplate."
            ),
            url="https://github.com/MwizerwaBit/mbitted",
            tags="FastAPI, React, Flutter, Postgres",
            featured=True,
        ),
        Project(
            slug="portfolio",
            title="This portfolio",
            description=(
                "A personal portfolio with a blog and an admin dashboard, built on "
                "the MwizerwaBit stack."
            ),
            url="https://github.com/MwizerwaBit/portfolio",
            tags="FastAPI, React, SQLite",
            featured=True,
        ),
        Project(
            slug="sample-app",
            title="FastAPI sample app",
            description=(
                "Reference implementation of the MwizerwaBit backend conventions: "
                "SQLAlchemy, Alembic, and CRUD endpoints."
            ),
            tags="FastAPI, Postgres, Alembic",
            featured=False,
        ),
    ]


def seed(db: Session) -> None:
    """Insert starter rows only if the tables are empty."""
    if db.scalar(select(Post).limit(1)) is not None:
        return
    db.add_all(_seed_posts() + _seed_projects())
    db.commit()
