# backend/app/core/config.py
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = "development"
    database_url: str | None = None
    print_mode: str = "text"
    admin_token: str | None = None
    session_close_time: str = "23:00"
    session_grace_minutes: int = 60
    session_timezone: str = "Asia/Bangkok"

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

    @field_validator("session_close_time")
    @classmethod
    def validate_session_close_time(cls, value: str) -> str:
        parts = value.split(":")
        if len(parts) != 2:
            raise ValueError("SESSION_CLOSE_TIME must be HH:MM.")
        hour, minute = parts
        if not hour.isdigit() or not minute.isdigit():
            raise ValueError("SESSION_CLOSE_TIME must be HH:MM.")
        h = int(hour)
        m = int(minute)
        if h < 0 or h > 23 or m < 0 or m > 59:
            raise ValueError("SESSION_CLOSE_TIME must be a valid time.")
        return value

    @field_validator("session_grace_minutes")
    @classmethod
    def validate_session_grace_minutes(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("SESSION_GRACE_MINUTES must be positive.")
        return value

    @field_validator("session_timezone")
    @classmethod
    def validate_session_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("SESSION_TIMEZONE must be a valid IANA timezone.") from exc
        return value


settings = Settings()
