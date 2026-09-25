from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SaúdeDados API"
    environment: str = "development"

    database_url: str = "postgresql+psycopg://saudedados:saudedados@localhost:5432/saudedados"

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    redis_url: str = "redis://localhost:6379/0"
    kpi_cache_ttl_seconds: int = 300

    s3_bucket_relatorios: str = "saudedados-relatorios"
    aws_region: str = "sa-east-1"

    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
