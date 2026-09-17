"""Application settings.

Convention: all configuration flows through this single ``Settings`` object,
populated from environment variables (and an optional ``.env`` file). No other
module should read ``os.environ`` directly.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Portfolio + Blog"
    api_v1_prefix: str = "/api/v1"

    # SQLite by default so the app runs with zero external services; set
    # DATABASE_URL to a Postgres DSN (e.g. postgresql+psycopg://...) to match
    # the production MwizerwaBit stack.
    database_url: str = "sqlite:///./portfolio.db"

    # Comma-separated list of origins allowed by CORS (local dev web server).
    cors_origins: str = "http://localhost:5173"

    # Public base URL used to build absolute links in the RSS feed and sitemap.
    app_url: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (read once per process)."""
    return Settings()


settings = get_settings()
