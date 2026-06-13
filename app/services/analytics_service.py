from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.url import URLAnalyticsResponse


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = AnalyticsRepository(session)

    async def get_url_analytics(self, alias: str) -> URLAnalyticsResponse:
        total_clicks = await self.repo.get_total_clicks(alias)
        daily = await self.repo.get_daily_stats(alias)
        return URLAnalyticsResponse(
            alias=alias,
            total_clicks=total_clicks,
            daily_clicks=[{"date": row.date.isoformat(), "clicks": row.clicks} for row in daily],
        )
