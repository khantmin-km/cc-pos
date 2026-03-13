# backend/app/schemas/waiter.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WaiterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    active: bool
    created_at: datetime


class WaiterCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class WaiterUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    active: bool | None = None

    @model_validator(mode="after")
    def ensure_at_least_one_field(self) -> "WaiterUpdateRequest":
        if self.name is None and self.active is None:
            raise ValueError("At least one field must be provided")
        return self
