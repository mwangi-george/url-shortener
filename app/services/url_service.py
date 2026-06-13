from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.url_validation import validate_public_url
from app.models.url import ShortURL
from app.repositories.url_repository import URLRepository
from app.schemas.url import CreateShortURLRequest, ShortURLResponse
from app.services.cache_service import URLCacheService
from app.services.id_generator import IDGenerator


class URLService:
    def __init__(self, session: AsyncSession, cache: URLCacheService) -> None:
        self.session = session
        self.repo = URLRepository(session)
        self.cache = cache
        self.id_generator = IDGenerator(session)

    async def create_short_url(self, payload: CreateShortURLRequest) -> ShortURLResponse:
        long_url = validate_public_url(str(payload.long_url))

        if payload.expires_at and payload.expires_at <= datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="expires_at is in the past")

        if payload.custom_alias:
            if await self.repo.alias_exists(payload.custom_alias):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="custom_alias already exists")
            next_id, alias = await self.id_generator.next_alias()
            alias = payload.custom_alias
        else:
            next_id, alias = await self.id_generator.next_alias()

        entity = ShortURL(
            id=next_id,
            alias=alias,
            long_url=long_url,
            expires_at=payload.expires_at,
        )

        try:
            created = await self.repo.create(entity)
        except IntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="alias already exists") from exc

        await self.cache.set_long_url(created.alias, created.long_url)

        return ShortURLResponse(
            id=created.id,
            alias=created.alias,
            short_url=f"{settings.base_url.rstrip('/')}/{created.alias}",
            long_url=created.long_url,
            created_at=created.created_at,
            expires_at=created.expires_at,
        )

    async def resolve_alias(self, alias: str) -> str | None:
        cached = await self.cache.get_long_url(alias)
        if cached:
            return cached

        if await self.cache.is_negative_cached(alias):
            return None

        entity = await self.repo.get_by_alias(alias)
        if entity is None or not URLRepository.is_resolvable(entity):
            await self.cache.set_not_found(alias)
            return None

        await self.cache.set_long_url(alias, entity.long_url)
        return entity.long_url
