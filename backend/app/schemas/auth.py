# backend/app/schemas/auth.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    pin: str = Field(min_length=1, max_length=50)


class LoginResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    token: str
    user_id: UUID
    username: str
    role: str
    expires_at: datetime
