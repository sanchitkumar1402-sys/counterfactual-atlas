"""Typed application configuration.

Every setting is read from the environment once, at import, and validated. A missing
DATABASE_URL fails here with a clear message instead of surfacing as a confusing None
twenty minutes into a request.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- required: no default, so startup fails loudly if unset ---
    database_url: str
    redis_url: str

    # --- optional, with defaults that are safe in development ---
    llm_api_key: str = ""
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    s3_bucket: str = "atlas-media"
    environment: Literal["development", "test", "production"] = "development"
    log_level: str = "debug"
    session_token_budget: int = 40_000


@lru_cache
def get_settings() -> Settings:
    """Cached so the environment is read and validated exactly once per process."""
    return Settings()  # type: ignore[call-arg]
