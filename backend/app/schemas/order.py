# backend/app/schemas/order.py
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrderConfirmItemRequest(BaseModel):
    menu_item_id: UUID
    quantity: int = Field(ge=1)


class OrderConfirmRequest(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=100)
    items: list[OrderConfirmItemRequest] = Field(min_length=1)


class OrderConfirmResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: UUID
    table_group_id: UUID
    order_item_ids: list[UUID]
