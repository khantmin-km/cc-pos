# backend/app/api/routers/orders.py
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.order import OrderConfirmRequest, OrderConfirmResponse
from app.services import order_service
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


@router.post(
    "/{physical_table_id}/orders/confirm",
    response_model=OrderConfirmResponse,
    dependencies=[Depends(get_current_user)],
)
def confirm_order(
    physical_table_id: UUID,
    request: OrderConfirmRequest,
    db: Session = Depends(get_db),
) -> OrderConfirmResponse:
    try:
        order_id, table_group_id, order_item_ids = order_service.confirm_order(
            db=db,
            physical_table_id=physical_table_id,
            idempotency_key=request.idempotency_key,
            items=request.items,
        )
        return OrderConfirmResponse(
            order_id=order_id,
            table_group_id=table_group_id,
            order_item_ids=order_item_ids,
        )
    except Exception as exc:
        _handle_error(exc)
        raise
