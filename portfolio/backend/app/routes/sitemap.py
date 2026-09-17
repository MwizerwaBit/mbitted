"""XML sitemap listing the public pages and published posts."""

from html import escape

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Post

router = APIRouter()


@router.get("/sitemap.xml")
def sitemap(db: Session = Depends(get_db)) -> Response:
    """Return a sitemap.xml for the home, blog, dashboard, and post pages."""
    paths = ["/", "/blog", "/dashboard"]

    posts = db.scalars(select(Post).where(Post.published == True)).all()  # noqa: E712
    paths.extend(f"/blog/{post.slug}" for post in posts)

    entries = "\n".join(
        f"  <url><loc>{escape(f'{settings.app_url}{path}', quote=False)}</loc></url>"
        for path in paths
    )

    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n"
    )

    return Response(content=body, media_type="application/xml")
