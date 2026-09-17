"""API schemas for the blog resource."""

from datetime import datetime

from pydantic import BaseModel


class Post(BaseModel):
    slug: str
    title: str
    summary: str
    body: str
    published_at: datetime
