# backend/app/schemas/audit_event.py
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=False)

    id: UUID
    actor_user_id: UUID
    actor_username: str
    actor_role: str
    event_type: str
    entity_type: str
    entity_id: UUID
    metadata: dict[str, Any]
    created_at: datetime
