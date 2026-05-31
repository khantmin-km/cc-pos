from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin_user
from app.schemas.modifier import (
    ModifierGroupCreateRequest,
    ModifierGroupResponse,
    ModifierGroupUpdateRequest,
    ModifierOptionCreateRequest,
    ModifierOptionResponse,
    ModifierOptionUpdateRequest,
)
from app.services import modifier_service
from app.services.errors import ConflictError, InvalidStateError, NotFoundError

router = APIRouter()


def _handle_error(exc: Exception) -> None:
    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, ConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, InvalidStateError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error")


@router.get(
    "/modifier-groups",
    response_model=list[ModifierGroupResponse],
    dependencies=[Depends(require_admin_user)],
)
def list_modifier_groups(db: Session = Depends(get_db)) -> list[ModifierGroupResponse]:
    return [ModifierGroupResponse.model_validate(group) for group in modifier_service.list_modifier_groups(db)]


@router.post(
    "/modifier-groups",
    response_model=ModifierGroupResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_user)],
)
def create_modifier_group(
    request: ModifierGroupCreateRequest,
    db: Session = Depends(get_db),
) -> ModifierGroupResponse:
    try:
        group = modifier_service.create_modifier_group(db, code=request.code, name=request.name)
        return ModifierGroupResponse.model_validate(group)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.get(
    "/modifier-groups/{modifier_group_id}",
    response_model=ModifierGroupResponse,
    dependencies=[Depends(require_admin_user)],
)
def get_modifier_group(modifier_group_id: UUID, db: Session = Depends(get_db)) -> ModifierGroupResponse:
    try:
        group = modifier_service.get_modifier_group(db, modifier_group_id)
        return ModifierGroupResponse.model_validate(group)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.patch(
    "/modifier-groups/{modifier_group_id}",
    response_model=ModifierGroupResponse,
    dependencies=[Depends(require_admin_user)],
)
def update_modifier_group(
    modifier_group_id: UUID,
    request: ModifierGroupUpdateRequest,
    db: Session = Depends(get_db),
) -> ModifierGroupResponse:
    try:
        group = modifier_service.update_modifier_group(
            db,
            modifier_group_id,
            name=request.name,
            is_active=request.is_active,
        )
        return ModifierGroupResponse.model_validate(group)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.get(
    "/modifier-groups/{modifier_group_id}/options",
    response_model=list[ModifierOptionResponse],
    dependencies=[Depends(require_admin_user)],
)
def list_modifier_options_by_group(
    modifier_group_id: UUID,
    db: Session = Depends(get_db),
) -> list[ModifierOptionResponse]:
    try:
        options = modifier_service.list_modifier_options_by_group(db, modifier_group_id)
        return [ModifierOptionResponse.model_validate(option) for option in options]
    except Exception as exc:
        _handle_error(exc)
        raise


@router.post(
    "/modifier-groups/{modifier_group_id}/options",
    response_model=ModifierOptionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_user)],
)
def create_modifier_option(
    modifier_group_id: UUID,
    request: ModifierOptionCreateRequest,
    db: Session = Depends(get_db),
) -> ModifierOptionResponse:
    try:
        option = modifier_service.create_modifier_option(
            db,
            modifier_group_id=modifier_group_id,
            code=request.code,
            label=request.label,
            price_delta=request.price_delta,
        )
        return ModifierOptionResponse.model_validate(option)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.get(
    "/modifier-options/{modifier_option_id}",
    response_model=ModifierOptionResponse,
    dependencies=[Depends(require_admin_user)],
)
def get_modifier_option(modifier_option_id: UUID, db: Session = Depends(get_db)) -> ModifierOptionResponse:
    try:
        option = modifier_service.get_modifier_option(db, modifier_option_id)
        return ModifierOptionResponse.model_validate(option)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.patch(
    "/modifier-options/{modifier_option_id}",
    response_model=ModifierOptionResponse,
    dependencies=[Depends(require_admin_user)],
)
def update_modifier_option(
    modifier_option_id: UUID,
    request: ModifierOptionUpdateRequest,
    db: Session = Depends(get_db),
) -> ModifierOptionResponse:
    try:
        option = modifier_service.update_modifier_option(
            db,
            modifier_option_id,
            label=request.label,
            price_delta=request.price_delta,
            is_active=request.is_active,
        )
        return ModifierOptionResponse.model_validate(option)
    except Exception as exc:
        _handle_error(exc)
        raise
