# backend/app/db/migrations/versions/9d1f0a2b7c31_add_order_item_serving_table.py
"""add order_item_serving table

Revision ID: 9d1f0a2b7c31
Revises: 3b7f2a4c1e90
Create Date: 2026-03-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "9d1f0a2b7c31"
down_revision: Union[str, Sequence[str], None] = "3b7f2a4c1e90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "order_item_serving",
        sa.Column("order_item_id", sa.UUID(), nullable=False),
        sa.Column("served_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["order_item_id"], ["order_items.id"]),
        sa.PrimaryKeyConstraint("order_item_id"),
    )


def downgrade() -> None:
    op.drop_table("order_item_serving")
