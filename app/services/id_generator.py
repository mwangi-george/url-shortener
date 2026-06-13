from __future__ import annotations

from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base62 import encode_base62

url_id_sequence = Sequence("short_url_id_seq")


class IDGenerator:
    """Database-backed ID generator.

    For massive multi-region deployments, replace this with Snowflake-style IDs,
    Redis INCR with allocation blocks, or a dedicated ID service.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def next_id(self) -> int:
        result = await self.session.execute(select(url_id_sequence.next_value()))
        return int(result.scalar_one())

    async def next_alias(self) -> tuple[int, str]:
        next_id = await self.next_id()
        return next_id, encode_base62(next_id)
