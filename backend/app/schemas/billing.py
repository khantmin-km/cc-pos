# backend/app/schemas/billing.py
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BillBreakdownResponse(BaseModel):
    table_group_id: UUID
    table_group_state: str
    items_total: Decimal
    adjustments_total: Decimal
    subtotal: Decimal
    tax_total: Decimal
    final_total: Decimal


class BillAdjustmentCreateRequest(BaseModel):
    amount: Decimal
    description: str = Field(min_length=1)
    reason: str | None = None
    reference_order_item_id: UUID | None = None
    category: str | None = None

    @model_validator(mode="after")
    def ensure_reason_for_negative(self) -> "BillAdjustmentCreateRequest":
        if self.amount < 0 and not self.reason:
            raise ValueError("Reason is required for negative adjustments")
        return self


class BillAdjustmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    table_group_id: UUID
    amount: Decimal
    description: str
    reason: str | None
    category: str | None
    created_by: str
    created_at: datetime
    reference_order_item_id: UUID | None
