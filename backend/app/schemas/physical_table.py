# backend/app/schemas/physical_table.py
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class PhysicalTableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    table_code: str
    current_table_group_id: UUID | None


class PhysicalTableOverviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    table_code: str
    current_table_group_id: UUID | None
    current_table_group_state: str | None
