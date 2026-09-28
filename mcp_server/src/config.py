from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    api_base_url: str = "http://localhost:8000/api/v1"
    email: Optional[str] = None
    password: Optional[str] = None
    access_token: Optional[str] = None
    timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(
        env_prefix="SMART_FINANCE_",
        env_file=(BASE_DIR / ".env", BASE_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
