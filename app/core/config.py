from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "url-shortener"
    app_env: Literal["local", "dev", "staging", "prod"] = "local"
    debug: bool = False
    base_url: str

    database_url: str
    redis_url: str

    cache_ttl_seconds: int = 60 * 60 * 24
    negative_cache_ttl_seconds: int = 60 * 5
    allowed_url_schemes: str = "http,https"
    log_level: str = "INFO"

    @property
    def allowed_schemes(self) -> set[str]:
        return {scheme.strip().lower() for scheme in self.allowed_url_schemes.split(",") if scheme}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

print(f"redis url: {settings.redis_url}")
