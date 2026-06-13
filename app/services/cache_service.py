from __future__ import annotations

from redis.asyncio import Redis

from app.core.config import settings


class URLCacheService:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    @staticmethod
    def _key(alias: str) -> str:
        return f"url:{alias}"

    async def get_long_url(self, alias: str) -> str | None:
        value = await self.redis.get(self._key(alias))
        if value == "__NOT_FOUND__":
            return None
        return value

    async def is_negative_cached(self, alias: str) -> bool:
        value = await self.redis.get(self._key(alias))
        return value == "__NOT_FOUND__"

    async def set_long_url(self, alias: str, long_url: str) -> None:
        await self.redis.set(self._key(alias), long_url, ex=settings.cache_ttl_seconds)

    async def set_not_found(self, alias: str) -> None:
        await self.redis.set(self._key(alias), "__NOT_FOUND__", ex=settings.negative_cache_ttl_seconds)

    async def delete(self, alias: str) -> None:
        await self.redis.delete(self._key(alias))
