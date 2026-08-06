from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database & Redis
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/smart_finance"
    REDIS_URL: str = "redis://redis:6379/0"

    # Security & Telegram
    SECRET_KEY: str = "super-secret-key-change-in-production"
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_ALLOWED_USER_IDS: List[int] = []

    # AI Credentials
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Financial Defaults
    DEFAULT_CURRENCY: str = "EUR"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
