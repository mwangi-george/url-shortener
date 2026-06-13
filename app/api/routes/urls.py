from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.redis import get_redis
from app.db.session import get_db_session
from app.schemas.url import (
    CreateShortURLRequest, 
    ShortURLResponse, 
    URLAnalyticsResponse,
)
from app.services.analytics_service import AnalyticsService
from app.services.cache_service import URLCacheService
from app.services.url_service import URLService

router = APIRouter()


@router.post("/urls", response_model=ShortURLResponse, status_code=201)
async def create_short_url(
    payload: CreateShortURLRequest,
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> ShortURLResponse:
    service = URLService(db, URLCacheService(redis))

    try:
        return await service.create_short_url(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/urls/{alias}/analytics", response_model=URLAnalyticsResponse)
async def get_url_analytics(
    alias: str,
    db: AsyncSession = Depends(get_db_session),
) -> URLAnalyticsResponse:
    service = AnalyticsService(db)

    try:
        return await service.get_url_analytics(alias)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
