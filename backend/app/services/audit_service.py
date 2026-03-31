# backend/app/services/audit_service.py
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories import audit_event_repo


EVENT_ORDER_ITEM_VOIDED = "ORDER_ITEM_VOIDED"
EVENT_ORDER_ITEM_SERVED = "ORDER_ITEM_SERVED"
EVENT_ORDER_ITEM_REPRINTED = "ORDER_ITEM_REPRINTED"
EVENT_ORDER_CONFIRMED = "ORDER_CONFIRMED"
EVENT_BILL_REQUESTED = "BILL_REQUESTED"
EVENT_BILL_MARKED_PAID = "BILL_MARKED_PAID"
EVENT_TABLE_CLOSED = "TABLE_CLOSED"
EVENT_BILL_ADJUSTMENT_CREATED = "BILL_ADJUSTMENT_CREATED"
EVENT_TABLE_SWITCHED = "TABLE_SWITCHED"
EVENT_TABLE_MERGED = "TABLE_MERGED"
EVENT_TABLE_SPLIT = "TABLE_SPLIT"
EVENT_TABLE_START_SERVICE = "TABLE_START_SERVICE"

ENTITY_ORDER_ITEM = "ORDER_ITEM"
ENTITY_ORDER = "ORDER"
ENTITY_TABLE_GROUP = "TABLE_GROUP"
ENTITY_BILL_ADJUSTMENT = "BILL_ADJUSTMENT"
ENTITY_PHYSICAL_TABLE = "PHYSICAL_TABLE"


def record_event(
    db: Session,
    *,
    actor,
    event_type: str,
    entity_type: str,
    entity_id: UUID,
    metadata: dict | None = None,
) -> None:
    if actor is None:
        return
    audit_event_repo.create_audit_event(
        db,
        actor_user_id=actor.id,
        actor_username=actor.username,
        actor_role=actor.role,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata=metadata or {},
    )


def list_events(
    db: Session,
    *,
    event_type: str | None = None,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    actor_user_id: UUID | None = None,
    limit: int = 50,
    offset: int = 0,
):
    return audit_event_repo.list_audit_events(
        db,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_user_id=actor_user_id,
        limit=limit,
        offset=offset,
    )
