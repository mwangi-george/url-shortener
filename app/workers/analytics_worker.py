from __future__ import annotations

import asyncio
from collections import Counter
from datetime import datetime

from loguru import logger
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import AsyncSessionLocal
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.url_repository import URLRepository
from app.services.analytics_queue import CLICK_GROUP, CLICK_STREAM

CONSUMER_NAME = "analytics-worker"
BATCH_SIZE = 500
BLOCK_MS = 5_000


async def ensure_group(redis: Redis) -> None:
    try:
        await redis.xgroup_create(CLICK_STREAM, CLICK_GROUP, id="0", mkstream=True)
    except Exception as exc:  # noqa: BLE001
        if "BUSYGROUP" not in str(exc):
            raise


async def process_batch(session: AsyncSession, messages: list[tuple[str, dict]]) -> None:
    counts_by_alias_day: Counter[tuple[str, str]] = Counter()
    counts_by_alias: Counter[str] = Counter()

    for _message_id, payload in messages:
        alias = payload.get("alias")
        clicked_at = payload.get("clicked_at")
        if not alias or not clicked_at:
            continue
        day = datetime.fromisoformat(clicked_at).date().isoformat()
        counts_by_alias_day[(alias, day)] += 1
        counts_by_alias[alias] += 1

    analytics_repo = AnalyticsRepository(session)
    url_repo = URLRepository(session)

    for (alias, day), count in counts_by_alias_day.items():
        await analytics_repo.increment_daily_clicks(alias, datetime.fromisoformat(day).date(), count)

    for alias, count in counts_by_alias.items():
        await url_repo.increment_click_count(alias, count)


async def run_worker() -> None:
    configure_logging()
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    await ensure_group(redis)
    logger.info("analytics_worker_started")

    while True:
        response = await redis.xreadgroup(
            groupname=CLICK_GROUP,
            consumername=CONSUMER_NAME,
            streams={CLICK_STREAM: ">"},
            count=BATCH_SIZE,
            block=BLOCK_MS,
        )
        if not response:
            continue

        stream_name, stream_messages = response[0]
        message_ids = [message_id for message_id, _ in stream_messages]

        async with AsyncSessionLocal() as session:
            try:
                await process_batch(session, stream_messages)
                await redis.xack(CLICK_STREAM, CLICK_GROUP, *message_ids)
            except Exception as exc:  # noqa: BLE001
                await session.rollback()
                logger.exception("analytics_batch_failed error={}", exc)


if __name__ == "__main__":
    asyncio.run(run_worker())
