# backend/app/api/routers/audit_events.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin_user
from app.schemas.audit_event import AuditEventResponse
from app.services import audit_service

router = APIRouter()


@router.get("", response_model=list[AuditEventResponse])
def list_audit_events(
    event_type: str | None = None,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    actor_user_id: UUID | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user=Depends(require_admin_user),
    db: Session = Depends(get_db),
) -> list[AuditEventResponse]:
    events = audit_service.list_events(
        db,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_user_id=actor_user_id,
        limit=limit,
        offset=offset,
    )
    return [
        AuditEventResponse(
            id=event.id,
            actor_user_id=event.actor_user_id,
            actor_username=event.actor_username,
            actor_role=event.actor_role,
            event_type=event.event_type,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            metadata=event.metadata_json,
            created_at=event.created_at,
        )
        for event in events
    ]
