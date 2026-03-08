# backend/app/api/routers/order_items.py
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services import order_item_service
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


@router.post("/{order_item_id}/void", status_code=status.HTTP_204_NO_CONTENT)
def void_order_item(order_item_id: UUID, db: Session = Depends(get_db)) -> Response:
    try:
        order_item_service.void_order_item(db, order_item_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.post("/{order_item_id}/mark-served", status_code=status.HTTP_204_NO_CONTENT)
def mark_order_item_served(order_item_id: UUID, db: Session = Depends(get_db)) -> Response:
    try:
        order_item_service.mark_order_item_served(db, order_item_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.post("/{order_item_id}/reprint", status_code=status.HTTP_204_NO_CONTENT)
def reprint_order_item(order_item_id: UUID, db: Session = Depends(get_db)) -> Response:
    try:
        order_item_service.reprint_order_item(db, order_item_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as exc:
        _handle_error(exc)
        raise
