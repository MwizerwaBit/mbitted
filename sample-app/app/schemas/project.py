"""Project resource: Pydantic schemas (create / update / read)."""

import uuid
from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMModel


class ProjectBase(ORMModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class ProjectCreate(ProjectBase):
    owner_id: uuid.UUID


class ProjectUpdate(ORMModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    owner_id: uuid.UUID | None = None


class ProjectRead(ProjectBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
