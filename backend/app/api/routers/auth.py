# backend/app/api/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.auth import LoginRequest, LoginResponse
from app.services import auth_service
from app.services.errors import UnauthorizedError

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    try:
        user, session = auth_service.login(db, username=request.username, pin=request.pin)
        return LoginResponse(
            token=session.token,
            user_id=user.id,
            username=user.username,
            role=user.role,
            expires_at=session.expires_at,
        )
    except UnauthorizedError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
