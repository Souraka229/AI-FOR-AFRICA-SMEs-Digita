"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the API service."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    jwt_secret: str = "dev-only-change-me-32chars-min!!"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    database_url: str = (
        "postgresql+asyncpg://afrosite:afrosite_dev_password@localhost:5432/afrosite_db"
    )
    # Bootstrap users for local smoke — passwords via env only, never in responses
    bootstrap_tenant_id: str = "tenant-demo-1"
    bootstrap_tenant_name: str = "Afrosite Demo"
    bootstrap_owner_email: str = "owner@afrosite.example"
    bootstrap_owner_password: str = "change-me-owner"
    bootstrap_cashier_email: str = "cashier@afrosite.example"
    bootstrap_cashier_password: str = "change-me-cashier"
    # Genius Pay sandbox — secrets via env only
    geniuspay_base_url: str = ""
    geniuspay_api_key: str = ""
    geniuspay_webhook_secret: str = ""
    geniuspay_create_path: str = "/v1/transactions"
    geniuspay_verify_path: str = "/v1/transactions/{provider_ref}"
    geniuspay_timeout_seconds: float = 15.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
