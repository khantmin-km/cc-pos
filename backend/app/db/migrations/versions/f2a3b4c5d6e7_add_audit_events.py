# backend/app/db/migrations/versions/f2a3b4c5d6e7_add_audit_events.py
"""add audit events

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2026-03-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f2a3b4c5d6e7"
down_revision: Union[str, Sequence[str], None] = "e1f2a3b4c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("actor_user_id", sa.UUID(), nullable=False),
        sa.Column("actor_username", sa.String(length=100), nullable=False),
        sa.Column("actor_role", sa.String(length=20), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.UUID(), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "event_type IN ("
            "'ORDER_ITEM_VOIDED',"
            "'ORDER_ITEM_SERVED',"
            "'ORDER_ITEM_REPRINTED',"
            "'ORDER_CONFIRMED',"
            "'BILL_REQUESTED',"
            "'BILL_MARKED_PAID',"
            "'TABLE_CLOSED',"
            "'BILL_ADJUSTMENT_CREATED',"
            "'TABLE_SWITCHED',"
            "'TABLE_MERGED',"
            "'TABLE_SPLIT',"
            "'TABLE_START_SERVICE'"
            ")",
            name="audit_event_type_check",
        ),
        sa.CheckConstraint(
            "entity_type IN ("
            "'ORDER_ITEM',"
            "'ORDER',"
            "'TABLE_GROUP',"
            "'BILL_ADJUSTMENT',"
            "'PHYSICAL_TABLE'"
            ")",
            name="audit_entity_type_check",
        ),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_events_created_at_id", "audit_events", ["created_at", "id"])
    op.create_index("ix_audit_events_event_type", "audit_events", ["event_type"])
    op.create_index("ix_audit_events_actor_user_id", "audit_events", ["actor_user_id"])
    op.create_index("ix_audit_events_entity", "audit_events", ["entity_type", "entity_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_events_entity", table_name="audit_events")
    op.drop_index("ix_audit_events_actor_user_id", table_name="audit_events")
    op.drop_index("ix_audit_events_event_type", table_name="audit_events")
    op.drop_index("ix_audit_events_created_at_id", table_name="audit_events")
    op.drop_table("audit_events")
