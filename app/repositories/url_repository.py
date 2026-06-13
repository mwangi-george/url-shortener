from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.url import ShortURL


class URLRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, url: ShortURL) -> ShortURL:
        self.session.add(url)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        await self.session.refresh(url)
        return url

    async def get_by_alias(self, alias: str) -> ShortURL | None:
        result = await self.session.execute(select(ShortURL).where(ShortURL.alias == alias))
        return result.scalar_one_or_none()

    async def alias_exists(self, alias: str) -> bool:
        result = await self.session.execute(select(ShortURL.id).where(ShortURL.alias == alias).limit(1))
        return result.scalar_one_or_none() is not None

    async def increment_click_count(self, alias: str, count: int) -> None:
        await self.session.execute(
            update(ShortURL).where(ShortURL.alias == alias).values(click_count=ShortURL.click_count + count)
        )
        await self.session.commit()

    @staticmethod
    def is_resolvable(url: ShortURL) -> bool:
        now = datetime.now(timezone.utc)
        return url.is_active and (url.expires_at is None or url.expires_at > now)
