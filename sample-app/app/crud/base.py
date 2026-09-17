"""Generic CRUD mixin.

Convention: every resource gets a thin CRUD class that subclasses
``CRUDBase`` and only adds resource-specific lookups. Shared operations live
here once; the scaffolder generates the thin subclass, not duplicated CRUD.
"""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    def get(self, db: Session, id: UUID) -> ModelType | None:
        return db.get(self.model, id)

    def list(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        return list(db.scalars(stmt))

    def create(self, db: Session, *, obj_in: dict[str, Any]) -> ModelType:
        obj = self.model(**obj_in)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, *, db_obj: ModelType, obj_in: dict[str, Any]) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, db_obj: ModelType) -> None:
        db.delete(db_obj)
        db.commit()
