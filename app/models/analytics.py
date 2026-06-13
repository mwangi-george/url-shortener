from __future__ import annotations

from datetime import date

from sqlalchemy import BigInteger, Date, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ClickDailyStat(Base):
    __tablename__ = "click_daily_stats"

    alias: Mapped[str] = mapped_column(String(32), primary_key=True)
    date: Mapped[date] = mapped_column(Date, primary_key=True)
    clicks: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
