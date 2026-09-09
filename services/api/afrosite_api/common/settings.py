"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the API service."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    jwt_secret: str = "dev-only-change-me-32chars-min!!"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    database_url: str = "postgresql+asyncpg://afrosite:afrosite_dev_password@localhost:5432/afrosite_db"
    # Bootstrap owner for local smoke (password never hardcoded in responses)
    bootstrap_owner_email: str = "owner@afrosite.example"
    bootstrap_owner_password: str = "change-me-owner"


@lru_cache
def get_settings() -> Settings:
    return Settings()
