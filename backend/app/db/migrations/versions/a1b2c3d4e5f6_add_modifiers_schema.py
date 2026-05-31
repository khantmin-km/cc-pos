"""add modifiers schema

Revision ID: a1b2c3d4e5f6
Revises: f2a3b4c5d6e7
Create Date: 2026-06-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f2a3b4c5d6e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "modifier_groups",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "modifier_options",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("modifier_group_id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("label", sa.String(length=200), nullable=False),
        sa.Column(
            "price_delta",
            sa.Numeric(precision=10, scale=2, asdecimal=True),
            server_default=sa.text("0.00"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["modifier_group_id"], ["modifier_groups.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("modifier_group_id", "code", name="uq_modifier_options_group_code"),
    )

    op.create_table(
        "menu_item_modifier_groups",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("menu_item_id", sa.UUID(), nullable=False),
        sa.Column("modifier_group_id", sa.UUID(), nullable=False),
        sa.Column("min_select", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("max_select", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("max_select >= 1", name="menu_item_modifier_groups_max_select_positive_check"),
        sa.CheckConstraint("max_select >= min_select", name="menu_item_modifier_groups_max_ge_min_check"),
        sa.CheckConstraint("min_select >= 0", name="menu_item_modifier_groups_min_select_check"),
        sa.ForeignKeyConstraint(["menu_item_id"], ["menu_items.id"]),
        sa.ForeignKeyConstraint(["modifier_group_id"], ["modifier_groups.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("menu_item_id", "modifier_group_id", name="uq_menu_item_modifier_groups_pair"),
    )

    op.create_table(
        "menu_item_modifier_group_options",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("menu_item_modifier_group_id", sa.UUID(), nullable=False),
        sa.Column("modifier_option_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["menu_item_modifier_group_id"], ["menu_item_modifier_groups.id"]),
        sa.ForeignKeyConstraint(["modifier_option_id"], ["modifier_options.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "menu_item_modifier_group_id",
            "modifier_option_id",
            name="uq_menu_item_modifier_group_options_pair",
        ),
    )

    op.add_column(
        "order_items",
        sa.Column("parent_order_item_id", sa.UUID(), nullable=True),
    )
    op.add_column(
        "order_items",
        sa.Column("modifier_group_name_snap", sa.String(length=200), nullable=True),
    )
    op.add_column(
        "order_items",
        sa.Column("modifier_option_label_snap", sa.String(length=200), nullable=True),
    )
    op.add_column(
        "order_items",
        sa.Column("kind", sa.String(length=20), server_default=sa.text("'MAIN'"), nullable=False),
    )
    op.create_foreign_key(
        "fk_order_items_parent_order_item_id",
        "order_items",
        "order_items",
        ["parent_order_item_id"],
        ["id"],
    )
    op.create_check_constraint(
        "order_item_kind_check",
        "order_items",
        "kind IN ('MAIN', 'MODIFIER')",
    )
    op.create_index("ix_order_items_parent_order_item_id", "order_items", ["parent_order_item_id"])
    op.create_index("ix_order_items_kind", "order_items", ["kind"])


def downgrade() -> None:
    op.drop_index("ix_order_items_kind", table_name="order_items")
    op.drop_index("ix_order_items_parent_order_item_id", table_name="order_items")
    op.drop_constraint("order_item_kind_check", "order_items", type_="check")
    op.drop_constraint("fk_order_items_parent_order_item_id", "order_items", type_="foreignkey")
    op.drop_column("order_items", "kind")
    op.drop_column("order_items", "modifier_option_label_snap")
    op.drop_column("order_items", "modifier_group_name_snap")
    op.drop_column("order_items", "parent_order_item_id")

    op.drop_table("menu_item_modifier_group_options")
    op.drop_table("menu_item_modifier_groups")
    op.drop_table("modifier_options")
    op.drop_table("modifier_groups")
