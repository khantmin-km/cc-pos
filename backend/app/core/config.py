# backend/app/core/config.py
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = "development"
    database_url: str | None = None
    print_mode: str = "text"
    session_ttl_hours: int = 12
    cors_allow_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str | None) -> str:
        if not value:
            raise ValueError("DATABASE_URL is required. Set it in .env or the environment.")
        return value

    @field_validator("print_mode")
    @classmethod
    def validate_print_mode(cls, value: str) -> str:
        if value not in {"text", "image"}:
            raise ValueError("PRINT_MODE must be 'text' or 'image'.")
        return value

    @field_validator("session_ttl_hours")
    @classmethod
    def validate_session_ttl_hours(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("SESSION_TTL_HOURS must be positive.")
        return value

    @field_validator("cors_allow_origins")
    @classmethod
    def validate_cors_allow_origins(cls, value: str) -> str:
        # Comma-separated list. Empty means "no CORS".
        return value.strip()


settings = Settings()
