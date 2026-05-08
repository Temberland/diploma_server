import os
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserRegister, UserLogin, TokenResponse, RefreshRequest, UserResponse
from app.services.auth import (
    get_user_by_email, verify_password, register_user,
    create_access_token, create_refresh_token,
    decode_token, blacklist_token, is_token_blacklisted, get_user_by_id
)
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter()
bearer_scheme = HTTPBearer()

TESTING = os.getenv("TESTING", "0") == "1"
limiter = Limiter(key_func=get_remote_address)


def rate_limit(limit: str):
    """Декоратор rate limit, который отключается в тестах"""
    def decorator(func):
        if TESTING:
            return func
        return limiter.limit(limit)(func)
    return decorator


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@rate_limit("5/minute")
def register(request: Request, data: UserRegister, db: Session = Depends(get_db)):
    if get_user_by_email(data.email, db):
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    user = register_user(data.email, data.password, data.currency, db)
    return TokenResponse(
        access_token=create_access_token({"sub": user.id}),
        refresh_token=create_refresh_token({"sub": user.id})
    )


@router.post("/login", response_model=TokenResponse)
@rate_limit("10/minute")
def login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(data.email, db)
    if not user or not verify_password(data.password, user.hash_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    return TokenResponse(
        access_token=create_access_token({"sub": user.id}),
        refresh_token=create_refresh_token({"sub": user.id})
    )


@router.post("/refresh", response_model=TokenResponse)
@rate_limit("10/minute")
def refresh(request: Request, data: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Невалидный refresh токен")
    if is_token_blacklisted(data.refresh_token, db):
        raise HTTPException(status_code=401, detail="Токен отозван")
    user = get_user_by_id(int(payload.get("sub")), db)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    blacklist_token(data.refresh_token, db)
    return TokenResponse(
        access_token=create_access_token({"sub": user.id}),
        refresh_token=create_refresh_token({"sub": user.id})
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    blacklist_token(credentials.credentials, db)
    return {"detail": "Выход выполнен"}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
