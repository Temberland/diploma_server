import os
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
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

HTML_SUCCESS = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Email подтверждён</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { height: 100%; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0a0a0f;
    min-height: 100vh;
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
  .left {
    background: #0f0f16;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 64px;
    text-align: center;
    border-right: 1px solid #1e1e2a;
    position: relative;
    overflow: hidden;
  }
  .left::before {
    content: '';
    position: absolute;
    bottom: -80px; left: -80px;
    width: 400px; height: 400px;
    border-radius: 50%;
    border: 1px solid rgba(232,82,42,0.12);
  }
  .left::after {
    content: '';
    position: absolute;
    bottom: -120px; left: -120px;
    width: 560px; height: 560px;
    border-radius: 50%;
    border: 1px solid rgba(232,82,42,0.06);
  }
  .icon-glow {
    position: relative;
    margin-bottom: 36px;
  }
  .icon-glow::before {
    content: '';
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 160px; height: 160px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(232,82,42,0.25) 0%, transparent 70%);
  }
  .icon-wrap {
    position: relative;
    width: 96px; height: 96px; border-radius: 26px;
    background: #E8522A;
    display: flex; align-items: center; justify-content: center;
  }
  .icon-wrap svg { width: 48px; height: 48px; stroke: #fff; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
  .label {
    font-size: 11px; font-weight: 700; color: #E8522A;
    text-transform: uppercase; letter-spacing: 3px;
    margin-bottom: 16px;
  }
  .left h1 { font-size: 44px; font-weight: 800; color: #fff; line-height: 1.15; margin-bottom: 18px; }
  .left p { font-size: 17px; color: #666; line-height: 1.7; max-width: 340px; }
  .right {
    background: #0d0d14;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 80px 72px;
  }
  .right-title {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 12px;
  }
  .right-title h2 { font-size: 34px; font-weight: 800; color: #fff; }
  .right-title .dot { width: 8px; height: 8px; border-radius: 50%; background: #E8522A; flex-shrink: 0; }
  .right > p { font-size: 16px; color: #666; line-height: 1.7; margin-bottom: 36px; }
  .steps { display: flex; flex-direction: column; gap: 14px; margin-bottom: 48px; }
  .step {
    background: #13131c;
    border: 1px solid #1e1e2a;
    border-radius: 16px;
    padding: 20px 24px;
    display: flex; align-items: center; gap: 20px;
  }
  .step-num {
    width: 40px; height: 40px; border-radius: 12px; flex-shrink: 0;
    background: #E8522A;
    color: #fff; font-size: 16px; font-weight: 800;
    display: flex; align-items: center; justify-content: center;
  }
  .step-text { font-size: 16px; color: #ccc; font-weight: 500; }
  .footer {
    border-top: 1px solid #1a1a24;
    padding-top: 28px;
    display: flex; align-items: center; gap: 14px;
  }
  .shield {
    width: 32px; height: 32px; border-radius: 10px;
    background: #13131c; border: 1px solid #1e1e2a;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  }
  .shield svg { width: 15px; height: 15px; stroke: #555; fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
  .footer p { font-size: 13px; color: #444; }

  @media (max-width: 900px) {
    body { grid-template-columns: 1fr; }
    .left { padding: 64px 32px 56px; border-right: none; border-bottom: 1px solid #1e1e2a; }
    .left h1 { font-size: 32px; }
    .right { padding: 56px 32px; }
    .right-title h2 { font-size: 26px; }
    .step-text { font-size: 15px; }
  }
</style>
</head>
<body>
  <div class="left">
    <div class="icon-glow">
      <div class="icon-wrap">
        <svg viewBox="0 0 24 24"><path d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      </div>
    </div>
    <div class="label">Финансовый трекер</div>
    <h1>Email подтверждён</h1>
    <p>Ваш аккаунт активирован и готов к использованию.</p>
  </div>
  <div class="right">
    <div class="right-title">
      <h2>Что дальше?</h2>
      <div class="dot"></div>
    </div>
    <p>Откройте приложение на телефоне и войдите с вашим email и паролем.</p>
    <div class="steps">
      <div class="step"><div class="step-num">1</div><div class="step-text">Откройте приложение на телефоне</div></div>
      <div class="step"><div class="step-num">2</div><div class="step-text">Войдите с вашим email и паролем</div></div>
      <div class="step"><div class="step-num">3</div><div class="step-text">Начните отслеживать финансы</div></div>
    </div>
    <div class="footer">
      <div class="shield"><svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>
      <p>Это письмо отправлено автоматически</p>
    </div>
  </div>
</body>
</html>"""

HTML_ERROR = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ошибка подтверждения</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { height: 100%; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0a0a0f;
    min-height: 100vh;
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
  .left {
    background: #0f0f16;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 64px;
    text-align: center;
    border-right: 1px solid #1e1e2a;
    position: relative;
    overflow: hidden;
  }
  .left::before {
    content: '';
    position: absolute;
    bottom: -80px; left: -80px;
    width: 400px; height: 400px;
    border-radius: 50%;
    border: 1px solid rgba(232,82,42,0.08);
  }
  .icon-glow {
    position: relative;
    margin-bottom: 36px;
  }
  .icon-glow::before {
    content: '';
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 160px; height: 160px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(232,82,42,0.15) 0%, transparent 70%);
  }
  .icon-wrap {
    position: relative;
    width: 96px; height: 96px; border-radius: 26px;
    background: #1a1018;
    border: 2px solid #E8522A;
    display: flex; align-items: center; justify-content: center;
  }
  .icon-wrap svg { width: 48px; height: 48px; stroke: #E8522A; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
  .label {
    font-size: 11px; font-weight: 700; color: #E8522A;
    text-transform: uppercase; letter-spacing: 3px;
    margin-bottom: 16px;
  }
  .left h1 { font-size: 44px; font-weight: 800; color: #fff; line-height: 1.15; margin-bottom: 18px; }
  .left p { font-size: 17px; color: #666; line-height: 1.7; max-width: 340px; }
  .right {
    background: #0d0d14;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 80px 72px;
  }
  .right-title { margin-bottom: 12px; }
  .right-title h2 { font-size: 34px; font-weight: 800; color: #fff; }
  .right > p { font-size: 16px; color: #666; line-height: 1.7; margin-bottom: 32px; }
  .hint {
    background: #13101a;
    border: 1px solid #2a1a20;
    border-left: 3px solid #E8522A;
    border-radius: 0 16px 16px 0;
    padding: 24px 28px;
    font-size: 16px; color: #999; line-height: 1.7;
    margin-bottom: 48px;
  }
  .footer {
    border-top: 1px solid #1a1a24;
    padding-top: 28px;
    display: flex; align-items: center; gap: 14px;
  }
  .shield {
    width: 32px; height: 32px; border-radius: 10px;
    background: #13131c; border: 1px solid #1e1e2a;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  }
  .shield svg { width: 15px; height: 15px; stroke: #555; fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
  .footer p { font-size: 13px; color: #444; }

  @media (max-width: 900px) {
    body { grid-template-columns: 1fr; }
    .left { padding: 64px 32px 56px; border-right: none; border-bottom: 1px solid #1e1e2a; }
    .left h1 { font-size: 32px; }
    .right { padding: 56px 32px; }
    .right-title h2 { font-size: 26px; }
  }
</style>
</head>
<body>
  <div class="left">
    <div class="icon-glow">
      <div class="icon-wrap">
        <svg viewBox="0 0 24 24"><path d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"/></svg>
      </div>
    </div>
    <div class="label">Финансовый трекер</div>
    <h1>Ссылка недействительна</h1>
    <p>Ссылка устарела или уже была использована ранее.</p>
  </div>
  <div class="right">
    <div class="right-title">
      <h2>Что пошло не так?</h2>
    </div>
    <p>Ссылки для подтверждения действительны 15 минут с момента регистрации. Возможно, вы перешли слишком поздно или ссылка уже использовалась.</p>
    <div class="hint">
      Зарегистрируйтесь повторно с тем же email — придёт новое письмо со свежей ссылкой.
    </div>
    <div class="footer">
      <div class="shield"><svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>
      <p>Это письмо отправлено автоматически</p>
    </div>
  </div>
</body>
</html>"""


def rate_limit(limit: str):
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


@router.get("/verify-email", response_class=HTMLResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    if not verify_email_token(token, db):
        return HTMLResponse(content=HTML_ERROR, status_code=400)
    return HTMLResponse(content=HTML_SUCCESS)


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
@rate_limit("3/minute")
async def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
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
    if not apply_reset_token(data.token, data.new_password, db):
        raise HTTPException(status_code=400, detail="Неверный или истёкший токен")
    return {"detail": "Пароль успешно изменён"}
