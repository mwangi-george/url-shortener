from __future__ import annotations

import hashlib

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.redis import get_redis
from app.db.session import get_db_session
from app.services.analytics_queue import AnalyticsQueue
from app.services.cache_service import URLCacheService
from app.services.url_service import URLService

router = APIRouter()


def hash_ip(ip: str | None) -> str | None:
    if not ip:
        return None
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()


@router.get("/{alias}")
async def redirect_alias(
    alias: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> RedirectResponse:
    service = URLService(db, URLCacheService(redis))
    long_url = await service.resolve_alias(alias)
    if long_url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")

    # Best-effort non-blocking-ish analytics. In a very strict hot path, push this through
    # a background task or UDP/local sidecar. Redis Streams is usually fast enough here.
    try:
        await AnalyticsQueue(redis).publish_click(
            alias=alias,
            ip_hash=hash_ip(request.client.host if request.client else None),
            user_agent=request.headers.get("user-agent"),
            referrer=request.headers.get("referer"),
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("failed_to_publish_click_event alias={} error={}", alias, exc)

    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)
