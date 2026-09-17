"""Portfolio projects endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectRead

router = APIRouter()


@router.get("", response_model=list[ProjectRead])
def list_projects(
    featured: bool | None = None, db: Session = Depends(get_db)
) -> list[Project]:
    """List projects, newest first. Optionally filter to featured only."""
    stmt = select(Project).order_by(Project.created_at.desc())
    if featured is not None:
        stmt = stmt.where(Project.featured == featured)
    return list(db.scalars(stmt).all())


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> Project:
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
