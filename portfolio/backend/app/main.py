"""FastAPI application entrypoint.

Run with: ``uvicorn app.main:app --reload``
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import seed
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routes import dashboard, feed, posts, projects, sitemap


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables and seed starter content on startup (SQLite for local dev;
    # swap DATABASE_URL + Alembic for Postgres in production).
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed.seed(db)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router, prefix=f"{settings.api_v1_prefix}/posts", tags=["posts"])
app.include_router(
    projects.router, prefix=f"{settings.api_v1_prefix}/projects", tags=["projects"]
)
app.include_router(
    dashboard.router, prefix=f"{settings.api_v1_prefix}/dashboard", tags=["dashboard"]
)

# SEO / syndication endpoints live at the app root (not under /api/v1).
app.include_router(feed.router, tags=["feed"])
app.include_router(sitemap.router, tags=["sitemap"])


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
