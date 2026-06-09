import os
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import (
    UserRegister, UserLogin, TokenResponse, RefreshRequest, UserResponse,
    ForgotPasswordRequest, ResetPasswordRequest,
)
from app.services.email import (
    create_verification_token, send_verification_email, verify_email_token,
    create_reset_token, send_reset_email, apply_reset_token,
)
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
async def register(request: Request, data: UserRegister, db: Session = Depends(get_db)):
    if get_user_by_email(data.email, db):
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    user = register_user(data.email, data.password, data.currency, db)
    # Отправляем письмо подтверждения; ошибка SMTP не ломает регистрацию
    try:
        ver_token = create_verification_token(user.id, db)
        await send_verification_email(user.email, ver_token)
    except Exception:
        pass
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


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Подтверждение email по токену из письма."""
    if not verify_email_token(token, db):
        raise HTTPException(status_code=400, detail="Неверный или истёкший токен")
    return {"detail": "Email подтверждён"}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
@rate_limit("3/minute")
async def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """Запрос сброса пароля. Всегда возвращает 200 — защита от email enumeration."""
    user = get_user_by_email(data.email, db)
    if user:
        try:
            reset_token = create_reset_token(user.id, db)
            await send_reset_email(user.email, reset_token)
        except Exception:
            pass
    return {"detail": "Если email зарегистрирован, ссылка для сброса отправлена"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Установка нового пароля по токену из письма."""
    if not apply_reset_token(data.token, data.new_password, db):
        raise HTTPException(status_code=400, detail="Неверный или истёкший токен")
    return {"detail": "Пароль успешно изменён"}
