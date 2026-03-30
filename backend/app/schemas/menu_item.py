# backend/app/schemas/menu_item.py
from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


MenuItemStatus = Literal["AVAILABLE", "UNAVAILABLE", "RETIRED"]


class MenuItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    price: Decimal
    category: str
    status: MenuItemStatus
    image_url: str | None = None
    created_at: datetime


class MenuItemCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    price: Decimal = Field(gt=0)
    category: str = Field(min_length=1, max_length=100)


class MenuItemUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    price: Decimal | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    status: MenuItemStatus | None = None

    @model_validator(mode="after")
    def ensure_at_least_one_field(self) -> "MenuItemUpdateRequest":
        if (
            self.name is None
            and self.price is None
            and self.status is None
            and self.category is None
        ):
            raise ValueError("At least one field must be provided")
        return self
