from __future__ import annotations

from datetime import datetime, timezone

from redis.asyncio import Redis

CLICK_STREAM = "click_events"
CLICK_GROUP = "analytics_workers"


class AnalyticsQueue:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def publish_click(
        self,
        *,
        alias: str,
        ip_hash: str | None = None,
        user_agent: str | None = None,
        referrer: str | None = None,
    ) -> None:
        await self.redis.xadd(
            CLICK_STREAM,
            {
                "alias": alias,
                "clicked_at": datetime.now(timezone.utc).isoformat(),
                "ip_hash": ip_hash or "",
                "user_agent": user_agent or "",
                "referrer": referrer or "",
            },
            maxlen=10_000_000,
            approximate=True,
        )
