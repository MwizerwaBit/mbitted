"""RSS 2.0 feed of published blog posts."""

import calendar
from datetime import datetime
from email.utils import formatdate
from html import escape

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Post

router = APIRouter()


def _rfc822(dt: datetime | None) -> str:
    """Format a naive-UTC datetime as an RFC 822 (GMT) date string."""
    if dt is None:
        return ""
    return formatdate(calendar.timegm(dt.timetuple()), localtime=False, usegmt=True)


@router.get("/feed.xml")
def rss_feed(db: Session = Depends(get_db)) -> Response:
    """Return a valid RSS 2.0 document for all published posts."""
    posts = db.scalars(
        select(Post)
        .where(Post.published == True)  # noqa: E712
        .order_by(Post.published_at.desc())
    ).all()

    items = []
    for post in posts:
        link = f"{settings.app_url}/blog/{escape(post.slug, quote=False)}"
        pub_date = _rfc822(post.published_at) or _rfc822(post.created_at)
        items.append(
            "        <item>\n"
            f"          <title>{escape(post.title)}</title>\n"
            f"          <link>{link}</link>\n"
            f"          <pubDate>{pub_date}</pubDate>\n"
            f"          <description>{escape(post.summary or '')}</description>\n"
            "        </item>"
        )

    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        "  <channel>\n"
        f"    <title>{escape(settings.app_name)}</title>\n"
        f"    <link>{escape(settings.app_url, quote=False)}</link>\n"
        f"    <description>Latest posts from {escape(settings.app_name)}.</description>\n"
        + "\n".join(items)
        + "\n"
        "  </channel>\n"
        "</rss>\n"
    )

    return Response(content=feed, media_type="application/rss+xml")
