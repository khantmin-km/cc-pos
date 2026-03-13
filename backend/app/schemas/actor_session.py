# backend/app/schemas/actor_session.py
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


ActorRole = Literal["WAITER", "ADMIN"]


class ActorSessionCreateRequest(BaseModel):
    role: ActorRole
    waiter_id: UUID | None = None
    actor_name: str | None = Field(default=None, min_length=1, max_length=100)

    @model_validator(mode="after")
    def validate_role(self) -> "ActorSessionCreateRequest":
        if self.role == "WAITER" and self.waiter_id is None:
            raise ValueError("waiter_id is required for WAITER sessions")
        return self


class ActorSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: ActorRole
    actor_name: str
    waiter_id: UUID | None
    started_at: datetime
    expires_at: datetime
    ended_at: datetime | None
