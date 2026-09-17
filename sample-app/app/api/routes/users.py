"""User resource: HTTP endpoints."""

import uuid

from fastapi import APIRouter, HTTPException, status

from app import crud
from app.api.deps import DBSession
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(*, db: DBSession, user_in: UserCreate) -> UserRead:
    existing = crud.user.get_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )
    return crud.user.create(db, obj_in=user_in.model_dump())


@router.get("", response_model=list[UserRead])
def list_users(*, db: DBSession, skip: int = 0, limit: int = 100) -> list[UserRead]:
    return crud.user.list(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
def get_user(*, db: DBSession, user_id: uuid.UUID) -> UserRead:
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(*, db: DBSession, user_id: uuid.UUID, user_in: UserUpdate) -> UserRead:
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return crud.user.update(db, db_obj=user, obj_in=user_in.model_dump(exclude_unset=True))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(*, db: DBSession, user_id: uuid.UUID) -> None:
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    crud.user.delete(db, db_obj=user)
