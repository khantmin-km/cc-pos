# backend/app/db/migrations/versions/3b7f2a4c1e90_add_menu_items_and_order_idempotency.py
"""add menu_items and order idempotency

Revision ID: 3b7f2a4c1e90
Revises: 68a9d8e37b59
Create Date: 2026-03-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3b7f2a4c1e90"
down_revision: Union[str, Sequence[str], None] = "68a9d8e37b59"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "menu_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "status IN ('AVAILABLE', 'UNAVAILABLE', 'RETIRED')",
            name="menu_item_status_check",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column("orders", sa.Column("idempotency_key", sa.String(length=100), nullable=True))
    op.execute("UPDATE orders SET idempotency_key = id::text WHERE idempotency_key IS NULL")
    op.alter_column("orders", "idempotency_key", nullable=False)
    op.create_unique_constraint("uq_orders_idempotency_key", "orders", ["idempotency_key"])


def downgrade() -> None:
    op.drop_constraint("uq_orders_idempotency_key", "orders", type_="unique")
    op.drop_column("orders", "idempotency_key")
    op.drop_table("menu_items")
