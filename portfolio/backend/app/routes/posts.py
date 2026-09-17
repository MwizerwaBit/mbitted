"""Blog posts CRUD endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Post
from app.schemas import PostCreate, PostRead, PostUpdate

router = APIRouter()


def _stamp_published_at(post: Post) -> None:
    """Set ``published_at`` the first time a post becomes published."""
    if post.published and post.published_at is None:
        post.published_at = datetime.now(timezone.utc).replace(tzinfo=None)


@router.get("", response_model=list[PostRead])
def list_posts(
    published: bool | None = None, db: Session = Depends(get_db)
) -> list[Post]:
    """List posts, newest first. Optionally filter by published state."""
    stmt = select(Post).order_by(Post.created_at.desc())
    if published is not None:
        stmt = stmt.where(Post.published == published)
    return list(db.scalars(stmt).all())


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(payload: PostCreate, db: Session = Depends(get_db)) -> Post:
    if db.scalar(select(Post).where(Post.slug == payload.slug)) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A post with this slug already exists.",
        )
    post = Post(**payload.model_dump())
    _stamp_published_at(post)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("/{slug}", response_model=PostRead)
def get_post(slug: str, db: Session = Depends(get_db)) -> Post:
    post = db.scalar(select(Post).where(Post.slug == slug))
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return post


@router.put("/{post_id}", response_model=PostRead)
def update_post(post_id: int, payload: PostUpdate, db: Session = Depends(get_db)) -> Post:
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(post, key, value)
    _stamp_published_at(post)
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)) -> None:
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    db.delete(post)
    db.commit()
