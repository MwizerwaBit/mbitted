"""Import every model here so ``app.models`` registers them on ``Base.metadata``.

Alembic autogenerate depends on this: it imports ``app.models`` and reads
``Base.metadata`` to diff against the live database. Any new model MUST be
added to this module (and to ``alembic/env.py``'s import) or autogenerate will
not see it.
"""

from app.models.project import Project
from app.models.user import User

__all__ = ["User", "Project"]
