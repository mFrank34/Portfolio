from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Settings(BaseSettings):
    secret_key = str
    database_url: str = "sqlite:///./site.db"
    sql_echo: bool = False
    cors_origins: list[str] = ["http://localhost:8000"]
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
