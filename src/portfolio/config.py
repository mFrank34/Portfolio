from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Settings(BaseSettings):
    secret_key: str
    admin_username: str  # Renamed from 'username' to avoid OS conflict
    password: str

    database_url: str = "sqlite+aiosqlite:///./portfolio.db"
    sql_echo: bool = False
    environment: str = "development"
    debug: bool

    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        for prefix in ("postgresql://", "postgres://"):
            if v.startswith(prefix):
                return "postgresql+asyncpg://" + v[len(prefix):]
        return v


settings = Settings()