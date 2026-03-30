# backend/app/api/routers/menu_items.py
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin_user
from app.schemas.menu_item import MenuItemCreateRequest, MenuItemResponse, MenuItemUpdateRequest
from app.services import menu_item_service
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
    response_model=list[MenuItemResponse],
    dependencies=[Depends(get_current_user)],
)
def list_menu_items(db: Session = Depends(get_db)) -> list[MenuItemResponse]:
    return [MenuItemResponse.model_validate(item) for item in menu_item_service.list_menu_items(db)]


@router.post(
    "",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_user)],
)
def create_menu_item(
    request: MenuItemCreateRequest,
    db: Session = Depends(get_db),
) -> MenuItemResponse:
    try:
        item = menu_item_service.create_menu_item(
            db,
            name=request.name,
            price=request.price,
            category=request.category,
        )
        return MenuItemResponse.model_validate(item)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.patch(
    "/{menu_item_id}",
    response_model=MenuItemResponse,
    dependencies=[Depends(require_admin_user)],
)
def update_menu_item(
    menu_item_id: UUID,
    request: MenuItemUpdateRequest,
    db: Session = Depends(get_db),
) -> MenuItemResponse:
    try:
        item = menu_item_service.update_menu_item(
            db=db,
            menu_item_id=menu_item_id,
            name=request.name,
            price=request.price,
            category=request.category,
            status=request.status,
        )
        return MenuItemResponse.model_validate(item)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.post(
    "/{menu_item_id}/retire",
    response_model=MenuItemResponse,
    dependencies=[Depends(require_admin_user)],
)
def retire_menu_item(menu_item_id: UUID, db: Session = Depends(get_db)) -> MenuItemResponse:
    try:
        item = menu_item_service.retire_menu_item(db, menu_item_id)
        return MenuItemResponse.model_validate(item)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.post(
    "/{menu_item_id}/image",
    response_model=MenuItemResponse,
    dependencies=[Depends(require_admin_user)],
)
def upload_menu_item_image(
    menu_item_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> MenuItemResponse:
    try:
        data = file.file.read()
        item = menu_item_service.update_menu_item_image(
            db,
            menu_item_id,
            content_type=file.content_type,
            data=data,
        )
        return MenuItemResponse.model_validate(item)
    except Exception as exc:
        _handle_error(exc)
        raise
