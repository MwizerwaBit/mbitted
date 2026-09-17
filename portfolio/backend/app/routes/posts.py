"""Blog resource: HTTP endpoints."""

from fastapi import APIRouter, HTTPException, status

from app import store
from app.schemas import Post

router = APIRouter()


@router.get("", response_model=list[Post])
def list_posts() -> list[Post]:
    return store.list_posts()


@router.get("/{slug}", response_model=Post)
def get_post(slug: str) -> Post:
    post = store.get_post(slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return post
