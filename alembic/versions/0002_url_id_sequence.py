"""url id sequence

Revision ID: 0002_url_id_sequence
Revises: 0001_initial
Create Date: 2026-06-13
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_url_id_sequence"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE IF NOT EXISTS short_url_id_seq START WITH 1000000 INCREMENT BY 1")


def downgrade() -> None:
    op.execute("DROP SEQUENCE IF EXISTS short_url_id_seq")
