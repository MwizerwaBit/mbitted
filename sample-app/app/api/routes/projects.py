"""Project resource: HTTP endpoints."""

import uuid

from fastapi import APIRouter, HTTPException, status

from app import crud
from app.api.deps import DBSession
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter()


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(*, db: DBSession, project_in: ProjectCreate) -> ProjectRead:
    if not crud.user.get(db, id=project_in.owner_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner user not found.",
        )
    return crud.project.create(db, obj_in=project_in.model_dump())


@router.get("", response_model=list[ProjectRead])
def list_projects(*, db: DBSession, skip: int = 0, limit: int = 100) -> list[ProjectRead]:
    return crud.project.list(db, skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(*, db: DBSession, project_id: uuid.UUID) -> ProjectRead:
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    *, db: DBSession, project_id: uuid.UUID, project_in: ProjectUpdate
) -> ProjectRead:
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    if project_in.owner_id is not None and not crud.user.get(db, id=project_in.owner_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner user not found.",
        )
    return crud.project.update(
        db, db_obj=project, obj_in=project_in.model_dump(exclude_unset=True)
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(*, db: DBSession, project_id: uuid.UUID) -> None:
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    crud.project.delete(db, db_obj=project)
