"""FastAPI application entrypoint.

Run with: ``uvicorn app.main:app --reload``
"""

from fastapi import FastAPI

from app.api.routes import projects, users
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(users.router, prefix=f"{settings.api_v1_prefix}/users", tags=["users"])
app.include_router(
    projects.router, prefix=f"{settings.api_v1_prefix}/projects", tags=["projects"]
)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
