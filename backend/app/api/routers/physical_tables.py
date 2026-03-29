# backend/app/api/routers/physical_tables.py
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.physical_table import PhysicalTableOverviewResponse, PhysicalTableResponse
from app.schemas.table_group import TableGroupResponse
from app.services import physical_table_service, table_group_service
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
    "",
    response_model=list[PhysicalTableResponse],
    dependencies=[Depends(get_current_user)],
)
def list_tables(db: Session = Depends(get_db)) -> list[PhysicalTableResponse]:
    rows = physical_table_service.list_tables(db)
    return [
        PhysicalTableResponse(id=table_id, table_code=code, current_table_group_id=group_id)
        for table_id, code, group_id in rows
    ]


@router.get(
    "/overview",
    response_model=list[PhysicalTableOverviewResponse],
    dependencies=[Depends(get_current_user)],
)
def list_table_overview(db: Session = Depends(get_db)) -> list[PhysicalTableOverviewResponse]:
    rows = physical_table_service.list_table_overview(db)
    return [
        PhysicalTableOverviewResponse(
            id=table_id,
            table_code=code,
            current_table_group_id=group_id,
            current_table_group_state=state,
        )
        for table_id, code, group_id, state in rows
    ]


@router.post(
    "/{physical_table_id}/start-service",
    response_model=TableGroupResponse,
    dependencies=[Depends(get_current_user)],
)
def start_service(physical_table_id: UUID, db: Session = Depends(get_db)) -> TableGroupResponse:
    try:
        group_id = table_group_service.start_service(db, physical_table_id)
        group = table_group_service.get_group(db, group_id)
        return TableGroupResponse(
            id=group[0],
            state=group[1],
            physical_table_ids=group[2],
            opened_at=group[3],
            closed_at=group[4],
        )
    except Exception as exc:
        _handle_error(exc)
        raise
