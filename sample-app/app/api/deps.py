"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

# Use ``db: DBSession`` as a keyword-only route parameter to get a session.
DBSession = Annotated[Session, Depends(get_db)]
