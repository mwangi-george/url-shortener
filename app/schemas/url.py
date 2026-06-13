from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, field_validator


class CreateShortURLRequest(BaseModel):
    long_url: HttpUrl
    custom_alias: str | None = Field(default=None, min_length=4, max_length=32)
    expires_at: datetime | None = None

    @field_validator("custom_alias")
    @classmethod
    def validate_alias(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value.replace("-", "").replace("_", "").isalnum():
            raise ValueError("custom_alias may only contain letters, digits, hyphen, and underscore")
        reserved = {"api", "health", "metrics", "docs", "redoc", "openapi.json"}
        if value.lower() in reserved:
            raise ValueError("custom_alias is reserved")
        return value


class ShortURLResponse(BaseModel):
    id: int
    alias: str
    short_url: str
    long_url: str
    created_at: datetime
    expires_at: datetime | None


class URLAnalyticsResponse(BaseModel):
    alias: str
    total_clicks: int
    daily_clicks: list[dict]
