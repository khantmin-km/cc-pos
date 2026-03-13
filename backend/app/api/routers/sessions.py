# backend/app/api/routers/sessions.py
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_actor_session, require_admin_token
from app.schemas.actor_session import ActorSessionCreateRequest, ActorSessionResponse
from app.services import actor_session_service
from app.services.errors import ConflictError, NotFoundError

router = APIRouter()


def _handle_error(exc: Exception) -> None:
    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, ConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error")


@router.post(
    "",
    response_model=ActorSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_session(
    request: ActorSessionCreateRequest,
    db: Session = Depends(get_db),
    x_admin_token: str | None = Header(default=None),
) -> ActorSessionResponse:
    if request.role == "ADMIN":
        require_admin_token(x_admin_token)
    try:
        if request.role == "ADMIN":
            session = actor_session_service.create_admin_session(db, actor_name=request.actor_name)
        else:
            session = actor_session_service.create_waiter_session(db, waiter_id=request.waiter_id)
        return ActorSessionResponse.model_validate(session)
    except Exception as exc:
        _handle_error(exc)
        raise


@router.post(
    "/{session_id}/end",
    status_code=status.HTTP_204_NO_CONTENT,
)
def end_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_session=Depends(require_actor_session),
) -> Response:
    if current_session.id != session_id and current_session.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot end this session")
    try:
        actor_session_service.end_session(db, session_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as exc:
        _handle_error(exc)
        raise
