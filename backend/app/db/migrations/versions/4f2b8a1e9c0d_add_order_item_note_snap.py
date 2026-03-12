# backend/app/db/migrations/versions/4f2b8a1e9c0d_add_order_item_note_snap.py
"""add order item note snapshot

Revision ID: 4f2b8a1e9c0d
Revises: 9d1f0a2b7c31
Create Date: 2026-03-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4f2b8a1e9c0d"
down_revision: Union[str, Sequence[str], None] = "9d1f0a2b7c31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("order_items", sa.Column("note_snap", sa.String(length=200), nullable=True))


def downgrade() -> None:
    op.drop_column("order_items", "note_snap")
