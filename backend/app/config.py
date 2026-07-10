from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[1]
_ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "SnapShot API"
    debug: bool = False

    database_url: str = "postgresql://postgres:postgres@localhost:5432/snapshot"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id: str = ""

    frontend_url: str = "http://localhost:3000"

    worker_api_key: str = "change-me-worker-key"
    api_base_url: str = "http://localhost:8000"

    # Local dev only — set false in production
    bypass_subscription_check: bool = False

    aws_region: str = "eu-north-1"
    s3_bucket_name: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_presign_expire_seconds: int = 3600


settings = Settings()
