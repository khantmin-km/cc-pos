from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ModifierGroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ModifierGroupCreateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)


class ModifierGroupUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    is_active: bool | None = None

    @model_validator(mode="after")
    def ensure_at_least_one_field(self) -> "ModifierGroupUpdateRequest":
        if self.name is None and self.is_active is None:
            raise ValueError("At least one field must be provided")
        return self


class ModifierOptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    modifier_group_id: UUID
    code: str
    label: str
    price_delta: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ModifierOptionCreateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=200)
    price_delta: Decimal = Field(ge=0)


class ModifierOptionUpdateRequest(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=200)
    price_delta: Decimal | None = Field(default=None, ge=0)
    is_active: bool | None = None

    @model_validator(mode="after")
    def ensure_at_least_one_field(self) -> "ModifierOptionUpdateRequest":
        if self.label is None and self.price_delta is None and self.is_active is None:
            raise ValueError("At least one field must be provided")
        return self


class MenuItemModifierGroupConfigRequest(BaseModel):
    modifier_group_id: UUID
    min_select: int = Field(ge=0)
    max_select: int = Field(ge=1)
    option_ids: list[UUID] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_min_max(self) -> "MenuItemModifierGroupConfigRequest":
        if self.max_select < self.min_select:
            raise ValueError("max_select must be greater than or equal to min_select")
        return self


class MenuItemModifierConfigReplaceRequest(BaseModel):
    groups: list[MenuItemModifierGroupConfigRequest] = Field(default_factory=list)


class MenuItemModifierGroupConfigResponse(BaseModel):
    modifier_group_id: UUID
    group_name: str
    min_select: int
    max_select: int
    option_ids: list[UUID]


class MenuItemModifierConfigResponse(BaseModel):
    groups: list[MenuItemModifierGroupConfigResponse]
