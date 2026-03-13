# backend/app/api/routers/waiters.py
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_db,
    require_actor_session,
    require_admin_session,
    require_admin_token,
)
from app.schemas.waiter import WaiterCreateRequest, WaiterResponse, WaiterUpdateRequest
from app.services import waiter_service
from app.services.errors import ConflictError, NotFoundError

router = APIRouter()


def _handle_error(exc: Exception) -> None:
    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, ConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error")


@router.get("", response_model=list[WaiterResponse])
def list_waiters(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    x_actor_session: str | None = Header(default=None),
    x_admin_token: str | None = Header(default=None),
) -> list[WaiterResponse]:
    waiters = waiter_service.list_waiters(db)
    if include_inactive:
        require_admin_token(x_admin_token)
        session = require_actor_session(x_actor_session, db)
        if session.role != "ADMIN":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin session required")
        return [WaiterResponse.model_validate(waiter) for waiter in waiters]
    return [WaiterResponse.model_validate(waiter) for waiter in waiters if waiter.active]


@router.post(
    "",
    response_model=WaiterResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_token), Depends(require_admin_session)],
)
def create_waiter(
    request: WaiterCreateRequest,
    db: Session = Depends(get_db),
) -> WaiterResponse:
    try:
        waiter = waiter_service.create_waiter(db, name=request.name)
        return WaiterResponse.model_validate(waiter)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.patch(
    "/{waiter_id}",
    response_model=WaiterResponse,
    dependencies=[Depends(require_admin_token), Depends(require_admin_session)],
)
def update_waiter(
    waiter_id: UUID,
    request: WaiterUpdateRequest,
    db: Session = Depends(get_db),
) -> WaiterResponse:
    try:
        waiter = waiter_service.update_waiter(
            db,
            waiter_id,
            name=request.name,
            active=request.active,
        )
        return WaiterResponse.model_validate(waiter)
    except Exception as exc:
        _handle_error(exc)
        raise
