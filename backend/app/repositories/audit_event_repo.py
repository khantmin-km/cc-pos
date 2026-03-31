# backend/app/repositories/audit_event_repo.py
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


def create_audit_event(
    db: Session,
    *,
    actor_user_id: UUID,
    actor_username: str,
    actor_role: str,
    event_type: str,
    entity_type: str,
    entity_id: UUID,
    metadata: dict,
) -> AuditEvent:
    event = AuditEvent(
        actor_user_id=actor_user_id,
        actor_username=actor_username,
        actor_role=actor_role,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_json=metadata,
    )
    db.add(event)
    db.flush()
    return event


def list_audit_events(
    db: Session,
    *,
    event_type: str | None = None,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    actor_user_id: UUID | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[AuditEvent]:
    stmt = select(AuditEvent)
    if event_type:
        stmt = stmt.where(AuditEvent.event_type == event_type)
    if entity_type:
        stmt = stmt.where(AuditEvent.entity_type == entity_type)
    if entity_id:
        stmt = stmt.where(AuditEvent.entity_id == entity_id)
    if actor_user_id:
        stmt = stmt.where(AuditEvent.actor_user_id == actor_user_id)
    stmt = stmt.order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc())
    stmt = stmt.limit(limit).offset(offset)
    return list(db.scalars(stmt))
