from __future__ import annotations

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.redis import get_redis
from app.db.session import get_db_session

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db_session), redis: Redis = Depends(get_redis)) -> dict:
    try:
        await db.execute(text("SELECT 1"))
        await redis.ping()
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "error_msg": str(exc)}
