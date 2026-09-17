"""User resource: Pydantic schemas (create / update / read)."""

import uuid
from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMModel


class UserBase(ORMModel):
    email: str = Field(min_length=3, max_length=255)
    full_name: str = Field(min_length=1, max_length=255)


class UserCreate(UserBase):
    pass


class UserUpdate(ORMModel):
    email: str | None = Field(default=None, min_length=3, max_length=255)
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    is_active: bool | None = None


class UserRead(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
