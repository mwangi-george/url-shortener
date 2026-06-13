from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import ClickDailyStat
from app.models.url import ShortURL


class AnalyticsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def increment_daily_clicks(self, alias: str, day: date, count: int) -> None:
        statement = insert(ClickDailyStat).values(alias=alias, date=day, clicks=count)
        statement = statement.on_conflict_do_update(
            index_elements=[ClickDailyStat.alias, ClickDailyStat.date],
            set_={"clicks": ClickDailyStat.clicks + count},
        )
        await self.session.execute(statement)
        await self.session.commit()

    async def get_daily_stats(self, alias: str) -> list[ClickDailyStat]:
        result = await self.session.execute(
            select(ClickDailyStat).where(ClickDailyStat.alias == alias).order_by(ClickDailyStat.date.asc())
        )
        return list(result.scalars().all())

    async def get_total_clicks(self, alias: str) -> int:
        result = await self.session.execute(select(ShortURL.click_count).where(ShortURL.alias == alias))
        return result.scalar_one_or_none() or 0
