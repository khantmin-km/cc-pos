# backend/app/schemas/table_group.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TableGroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    state: str
    physical_table_ids: list[UUID]
    opened_at: datetime
    closed_at: datetime | None


class TableGroupTableRequest(BaseModel):
    physical_table_id: UUID


class SwitchTableRequest(BaseModel):
    from_table_id: UUID
    to_table_id: UUID


class MergeTableGroupsRequest(BaseModel):
    source_group_id: UUID
    target_group_id: UUID


class SplitTableGroupRequest(BaseModel):
    physical_table_ids: list[UUID]
