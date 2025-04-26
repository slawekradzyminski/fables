from functools import lru_cache
from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings using Pydantic BaseSettings."""
    openai_api_key: str = "test-key"  # Default for tests
    cors_allowed_origins: List[str] = ["*"]
    log_level: str = "INFO"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings() 