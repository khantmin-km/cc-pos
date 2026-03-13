# backend/app/core/config.py
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = "development"
    database_url: str | None = None
    print_mode: str = "text"
    admin_token: str | None = None

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

    @field_validator("admin_token")
    @classmethod
    def validate_admin_token(cls, value: str | None) -> str | None:
        if value is None or value.strip() == "":
            raise ValueError("ADMIN_TOKEN is required. Set it in .env or the environment.")
        return value


settings = Settings()
