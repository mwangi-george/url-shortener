"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-13
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "short_urls",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("alias", sa.String(length=32), nullable=False),
        sa.Column("long_url", sa.Text(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("click_count", sa.BigInteger(), server_default=sa.text("0"), nullable=False),
    )
    op.create_index("ix_short_urls_alias", "short_urls", ["alias"], unique=True)
    op.create_index("ix_short_urls_user_id", "short_urls", ["user_id"])
    op.create_index("ix_short_urls_created_at", "short_urls", ["created_at"])

    op.create_table(
        "click_daily_stats",
        sa.Column("alias", sa.String(length=32), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("clicks", sa.BigInteger(), server_default=sa.text("0"), nullable=False),
        sa.PrimaryKeyConstraint("alias", "date"),
    )


def downgrade() -> None:
    op.drop_table("click_daily_stats")
    op.drop_index("ix_short_urls_created_at", table_name="short_urls")
    op.drop_index("ix_short_urls_user_id", table_name="short_urls")
    op.drop_index("ix_short_urls_alias", table_name="short_urls")
    op.drop_table("short_urls")
