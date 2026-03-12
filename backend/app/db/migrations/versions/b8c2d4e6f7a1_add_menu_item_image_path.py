# backend/app/db/migrations/versions/b8c2d4e6f7a1_add_menu_item_image_path.py
"""add menu item image path

Revision ID: b8c2d4e6f7a1
Revises: 4f2b8a1e9c0d
Create Date: 2026-03-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b8c2d4e6f7a1"
down_revision: Union[str, Sequence[str], None] = "4f2b8a1e9c0d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("menu_items", sa.Column("image_path", sa.String(length=300), nullable=True))


def downgrade() -> None:
    op.drop_column("menu_items", "image_path")
