"""Pydantic schemas for API request/response bodies."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer


def _iso(dt: datetime) -> str:
    """Serialize a naive-UTC datetime as an ISO-8601 string with a ``Z`` suffix."""
    return dt.isoformat() + "Z"


class PostBase(BaseModel):
    slug: str
    title: str
    summary: str = ""
    body: str = ""


class PostCreate(PostBase):
    published: bool = True


class PostUpdate(BaseModel):
    slug: str | None = None
    title: str | None = None
    summary: str | None = None
    body: str | None = None
    published: bool | None = None


class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    summary: str
    body: str
    published: bool
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @field_serializer("published_at", "created_at", "updated_at")
    def _serialize_dt(self, dt: datetime | None) -> str | None:
        if dt is None:
            return None
        return _iso(dt)


class ProjectBase(BaseModel):
    slug: str
    title: str
    description: str = ""
    url: str | None = None
    tags: str = ""
    featured: bool = False


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    description: str
    url: str | None
    tags: str
    featured: bool
    created_at: datetime

    @field_serializer("created_at")
    def _serialize_created(self, dt: datetime) -> str:
        return _iso(dt)


class DashboardStats(BaseModel):
    total_posts: int
    published_posts: int
    draft_posts: int
    total_projects: int
    recent_posts: list[PostRead]
