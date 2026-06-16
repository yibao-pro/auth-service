from __future__ import annotations

from functools import lru_cache

try:
    from pydantic import Field
    from pydantic_settings import BaseSettings
except ModuleNotFoundError:  # pragma: no cover
    from pydantic.v1 import BaseSettings, Field


class Settings(BaseSettings):
    api_prefix: str = ""
    cors_origins: list[str] = ["*"]
    auth_service_host: str = Field(default="0.0.0.0", env="AUTH_SERVICE_HOST")
    auth_service_port: int = Field(default=8004, env="AUTH_SERVICE_PORT")
    database_url: str = Field(default="", env="DATABASE_URL")
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_user: str = Field(default="yibao_user", env="POSTGRES_USER")
    postgres_password: str = Field(default="123456", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="yibao_auth", env="POSTGRES_DB")
    postgres_admin_db: str = Field(default="postgres", env="POSTGRES_ADMIN_DB")
    jwt_secret_key: str = Field(
        default="dev-secret-change-me",
        env="JWT_SECRET_KEY",
        description="Default is for development only. Override in production.",
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=60, env="JWT_EXPIRE_MINUTES")

    class Config:
        env_prefix = "VOICE_APP_"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
