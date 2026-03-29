# backend/app/schemas/table_group.py
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ServedFilter(str, Enum):
    all = "all"
    served = "served"
    unserved = "unserved"


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


class TableGroupOrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    physical_table_id: UUID
    table_code: str
    menu_item_id: UUID | None
    menu_item_name: str
    unit_price: Decimal
    note: str | None
    status: str
    served_at: datetime | None
    created_at: datetime
    voided_at: datetime | None
