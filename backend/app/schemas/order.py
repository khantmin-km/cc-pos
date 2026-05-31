# backend/app/schemas/order.py
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrderModifierSelectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    modifier_group_id: UUID
    selected_option_ids: list[UUID] = Field(default_factory=list)


class OrderConfirmItemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    client_line_id: str = Field(min_length=1, max_length=100)
    menu_item_id: UUID
    note: str | None = Field(default=None, max_length=200)
    modifier_selections: list[OrderModifierSelectionRequest] = Field(default_factory=list)


class OrderConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    idempotency_key: str = Field(min_length=1, max_length=100)
    items: list[OrderConfirmItemRequest] = Field(min_length=1)


class OrderConfirmResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: UUID
    table_group_id: UUID
    order_item_ids: list[UUID]
