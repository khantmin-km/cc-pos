# backend/app/api/routers/table_groups.py
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin_token
from app.schemas.billing import (
    BillAdjustmentCreateRequest,
    BillAdjustmentResponse,
    BillBreakdownResponse,
)
from app.schemas.table_group import (
    MergeTableGroupsRequest,
    SplitTableGroupRequest,
    SwitchTableRequest,
    TableGroupResponse,
    TableGroupTableRequest,
)
from app.services import billing_service, table_group_service
from app.services.errors import ConflictError, InvalidStateError, NotFoundError, SplitNotAllowedError

router = APIRouter()


def _handle_error(exc: Exception) -> None:
    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, ConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, InvalidStateError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if isinstance(exc, SplitNotAllowedError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error")


def _to_response(group: tuple[UUID, str, list[UUID], object, object]) -> TableGroupResponse:
    return TableGroupResponse(
        id=group[0],
        state=group[1],
        physical_table_ids=group[2],
        opened_at=group[3],
        closed_at=group[4],
    )


@router.get("/open", response_model=list[TableGroupResponse])
def list_open_groups(db: Session = Depends(get_db)) -> list[TableGroupResponse]:
    groups = table_group_service.list_open_groups(db)
    return [_to_response(group) for group in groups]


@router.get("/{table_group_id}", response_model=TableGroupResponse)
def get_group(table_group_id: UUID, db: Session = Depends(get_db)) -> TableGroupResponse:
    try:
        group = table_group_service.get_group(db, table_group_id)
        return _to_response(group)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.get(
    "/{table_group_id}/bill",
    response_model=BillBreakdownResponse,
    dependencies=[Depends(require_admin_token)],
)
def get_bill(table_group_id: UUID, db: Session = Depends(get_db)) -> BillBreakdownResponse:
    try:
        breakdown = billing_service.get_bill_breakdown(db, table_group_id)
        return BillBreakdownResponse(**breakdown)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.post(
    "/{table_group_id}/bill-adjustments",
    response_model=BillAdjustmentResponse,
    dependencies=[Depends(require_admin_token)],
)
def create_bill_adjustment(
    table_group_id: UUID,
    request: BillAdjustmentCreateRequest,
    db: Session = Depends(get_db),
) -> BillAdjustmentResponse:
    try:
        adjustment = billing_service.create_bill_adjustment(
            db,
            table_group_id,
            amount=request.amount,
            description=request.description,
            reason=request.reason,
            created_by=request.created_by,
            reference_order_item_id=request.reference_order_item_id,
            category=request.category,
        )
        return BillAdjustmentResponse.model_validate(adjustment)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.post("/{table_group_id}/request-bill")
def request_bill(table_group_id: UUID, db: Session = Depends(get_db)) -> None:
    try:
        table_group_service.request_bill(db, table_group_id)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.post(
    "/{table_group_id}/mark-paid",
    dependencies=[Depends(require_admin_token)],
)
def mark_paid(table_group_id: UUID, db: Session = Depends(get_db)) -> None:
    try:
        table_group_service.mark_paid(db, table_group_id)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.post(
    "/{table_group_id}/close",
    dependencies=[Depends(require_admin_token)],
)
def close_group(table_group_id: UUID, db: Session = Depends(get_db)) -> None:
    try:
        table_group_service.close_group(db, table_group_id)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.post("/{table_group_id}/tables/add")
def add_table(
    table_group_id: UUID,
    request: TableGroupTableRequest,
    db: Session = Depends(get_db),
) -> None:
    try:
        table_group_service.attach_table(db, table_group_id, request.physical_table_id)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.post("/{table_group_id}/tables/remove")
def remove_table(
    table_group_id: UUID,
    request: TableGroupTableRequest,
    db: Session = Depends(get_db),
) -> None:
    try:
        table_group_service.detach_table(db, table_group_id, request.physical_table_id)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.post("/{table_group_id}/switch")
def switch_table(
    table_group_id: UUID,
    request: SwitchTableRequest,
    db: Session = Depends(get_db),
) -> None:
    try:
        table_group_service.switch_table(
            db, table_group_id, request.from_table_id, request.to_table_id
        )
    except Exception as exc:
        _handle_error(exc)
        raise


@router.post("/merge")
def merge_groups(request: MergeTableGroupsRequest, db: Session = Depends(get_db)) -> None:
    try:
        table_group_service.merge_groups(db, request.source_group_id, request.target_group_id)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.post(
    "/{table_group_id}/split",
    response_model=TableGroupResponse,
    dependencies=[Depends(require_admin_token)],
)
def split_group(
    table_group_id: UUID,
    request: SplitTableGroupRequest,
    db: Session = Depends(get_db),
) -> TableGroupResponse:
    try:
        new_group_id = table_group_service.split_group(db, table_group_id, request.physical_table_ids)
        group = table_group_service.get_group(db, new_group_id)
        return _to_response(group)
    except Exception as exc:
        _handle_error(exc)
        raise
