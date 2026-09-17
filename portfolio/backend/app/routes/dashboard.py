"""Dashboard endpoints: aggregate stats for the admin view."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Post, Project
from app.schemas import DashboardStats, PostRead

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
def stats(db: Session = Depends(get_db)) -> DashboardStats:
    total_posts = db.scalar(select(func.count()).select_from(Post)) or 0
    published_posts = (
        db.scalar(select(func.count()).select_from(Post).where(Post.published.is_(True)))
        or 0
    )
    total_projects = db.scalar(select(func.count()).select_from(Project)) or 0

    recent = list(
        db.scalars(select(Post).order_by(Post.created_at.desc()).limit(5)).all()
    )

    return DashboardStats(
        total_posts=total_posts,
        published_posts=published_posts,
        draft_posts=total_posts - published_posts,
        total_projects=total_projects,
        recent_posts=[PostRead.model_validate(p) for p in recent],
    )
