# backend/app/db/migrations/versions/e1f2a3b4c5d6_add_menu_item_category.py
"""add menu item category

Revision ID: e1f2a3b4c5d6
Revises: d4e5f6a7b8c9
Create Date: 2026-03-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "menu_items",
        sa.Column("category", sa.String(length=100), server_default="Uncategorized", nullable=False),
    )
    op.alter_column("menu_items", "category", server_default=None)


def downgrade() -> None:
    op.drop_column("menu_items", "category")
