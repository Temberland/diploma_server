import uuid
from datetime import datetime, timedelta
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from sqlalchemy.orm import Session
from app.config import settings
from app.models.email_token import EmailVerification, PasswordResetToken

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=465,
    MAIL_SERVER="smtp.yandex.ru",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
)

fastmail = FastMail(mail_config)
TOKEN_TTL_MINUTES = 15


def _generate_token() -> str:
    return uuid.uuid4().hex + uuid.uuid4().hex


def _verification_html(link: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Подтвердите email</title>
</head>
<body style="margin:0;padding:0;background:#0e0e0e;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0e0e0e;padding:48px 16px;">
    <tr><td align="center">
      <table width="540" cellpadding="0" cellspacing="0" style="background:#1a1a1f;border-radius:24px;border:1px solid #2e2e38;overflow:hidden;">

        <tr>
          <td align="center" style="padding:48px 48px 0;">
            
            <div style="font-size:11px;font-weight:700;color:#E8522A;text-transform:uppercase;letter-spacing:2.5px;margin-bottom:14px;">Финансовый трекер</div>
            <h1 style="margin:0 0 16px;color:#ffffff;font-size:30px;font-weight:800;line-height:1.2;">Подтвердите ваш email</h1>
            <p style="margin:0;font-size:15px;color:#888;line-height:1.75;max-width:380px;">
              Вы зарегистрировались в приложении. Для активации аккаунта нажмите кнопку ниже. Ссылка действительна <strong style="color:#ddd;">{TOKEN_TTL_MINUTES} минут</strong>.
            </p>
          </td>
        </tr>

        <tr>
          <td align="center" style="padding:36px 48px 32px;">
            <a href="{link}" style="display:inline-flex;align-items:center;gap:10px;background:#E8522A;color:#ffffff;text-decoration:none;font-size:17px;font-weight:700;padding:18px 40px;border-radius:14px;letter-spacing:0.2px;">
              Подтвердить email &nbsp;›
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </a>
          </td>
        </tr>

        <tr>
          <td style="padding:0 48px 28px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="border-top:1px solid #2a2a30;padding-top:24px;">
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td width="24" style="vertical-align:top;padding-top:2px;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#E8522A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                          <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
                        </svg>
                      </td>
                      <td style="padding-left:10px;">
                        <p style="margin:0 0 8px;font-size:13px;color:#555;">Если кнопка не работает, скопируйте ссылку:</p>
                        <a href="{link}" style="font-size:13px;color:#E8522A;word-break:break-all;text-decoration:none;">{link}</a>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <tr>
          <td style="background:#13131a;padding:20px 48px;border-top:1px solid #22222a;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td width="32" style="vertical-align:middle;">
                  <div style="width:28px;height:28px;border-radius:8px;background:#222;display:inline-flex;align-items:center;justify-content:center;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    </svg>
                  </div>
                </td>
                <td style="padding-left:12px;">
                  <p style="margin:0;font-size:12px;color:#a3a2a2;line-height:1.6;">
                    <strong style="color:#555;">Финансовый трекер</strong> &nbsp;·&nbsp; Если вы не регистрировались — проигнорируйте это письмо
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _reset_html(link: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Сброс пароля</title>
</head>
<body style="margin:0;padding:0;background:#0e0e0e;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0e0e0e;padding:48px 16px;">
    <tr><td align="center">
      <table width="540" cellpadding="0" cellspacing="0" style="background:#1a1a1f;border-radius:24px;border:1px solid #2e2e38;overflow:hidden;">

        <tr>
          <td align="center" style="padding:48px 48px 0;">
            
            <div style="font-size:11px;font-weight:700;color:#E8522A;text-transform:uppercase;letter-spacing:2.5px;margin-bottom:14px;">Финансовый трекер</div>
            <h1 style="margin:0 0 16px;color:#ffffff;font-size:30px;font-weight:800;line-height:1.2;">Сброс пароля</h1>
            <p style="margin:0;font-size:15px;color:#888;line-height:1.75;max-width:380px;">
              Мы получили запрос на сброс пароля. Ссылка действительна <strong style="color:#ddd;">{TOKEN_TTL_MINUTES} минут</strong>. Если вы не запрашивали сброс — просто проигнорируйте письмо.
            </p>
          </td>
        </tr>

        <tr>
          <td align="center" style="padding:36px 48px 32px;">
            <a href="{link}" style="display:inline-flex;align-items:center;gap:10px;background:#E8522A;color:#ffffff;text-decoration:none;font-size:17px;font-weight:700;padding:18px 40px;border-radius:14px;">
              Сбросить пароль &nbsp;›
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </a>
          </td>
        </tr>

        <tr>
          <td style="padding:0 48px 28px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="border-top:1px solid #2a2a30;padding-top:24px;">
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td width="24" style="vertical-align:top;padding-top:2px;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#E8522A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                          <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
                        </svg>
                      </td>
                      <td style="padding-left:10px;">
                        <p style="margin:0 0 8px;font-size:13px;color:#555;">Если кнопка не работает, скопируйте ссылку:</p>
                        <a href="{link}" style="font-size:13px;color:#E8522A;word-break:break-all;text-decoration:none;">{link}</a>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <tr>
          <td style="background:#13131a;padding:20px 48px;border-top:1px solid #22222a;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td width="32" style="vertical-align:middle;">
                  <div style="width:28px;height:28px;border-radius:8px;background:#222;display:inline-flex;align-items:center;justify-content:center;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    </svg>
                  </div>
                </td>
                <td style="padding-left:12px;">
                  <p style="margin:0;font-size:12px;color:#a3a2a2;line-height:1.6;">
                    <strong style="color:#555;">Финансовый трекер</strong> &nbsp;·&nbsp; Это письмо отправлено автоматически
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


# ── Верификация email ──────────────────────────────────────────────────────────

def create_verification_token(user_id: int, db: Session) -> str:
    db.query(EmailVerification).filter(
        EmailVerification.user_id == user_id,
        EmailVerification.is_used == False,
    ).update({"is_used": True})
    token = _generate_token()
    db.add(EmailVerification(
        user_id=user_id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(minutes=TOKEN_TTL_MINUTES),
    ))
    db.commit()
    return token


async def send_verification_email(email: str, token: str) -> None:
    link = f"{settings.FRONTEND_URL}/auth/verify-email?token={token}"
    message = MessageSchema(
        subject="Подтвердите ваш email — Финансовый трекер",
        recipients=[email],
        body=_verification_html(link),
        subtype=MessageType.html,
    )
    await fastmail.send_message(message)


def verify_email_token(token: str, db: Session) -> bool:
    from app.models.user import User
    record = db.query(EmailVerification).filter(
        EmailVerification.token == token,
        EmailVerification.is_used == False,
    ).first()
    if not record or record.expires_at < datetime.utcnow():
        return False
    record.is_used = True
    db.query(User).filter(User.id == record.user_id).update({"is_email_verified": True})
    db.commit()
    return True


# ── Сброс пароля ───────────────────────────────────────────────────────────────

def create_reset_token(user_id: int, db: Session) -> str:
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user_id,
        PasswordResetToken.is_used == False,
    ).update({"is_used": True})
    token = _generate_token()
    db.add(PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(minutes=TOKEN_TTL_MINUTES),
    ))
    db.commit()
    return token


async def send_reset_email(email: str, token: str) -> None:
    link = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
    message = MessageSchema(
        subject="Сброс пароля — Финансовый трекер",
        recipients=[email],
        body=_reset_html(link),
        subtype=MessageType.html,
    )
    await fastmail.send_message(message)


def apply_reset_token(token: str, new_password: str, db: Session) -> bool:
    from app.models.user import User
    from app.services.auth import hash_password
    record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.is_used == False,
    ).first()
    if not record or record.expires_at < datetime.utcnow():
        return False
    record.is_used = True
    db.query(User).filter(User.id == record.user_id).update(
        {"hash_password": hash_password(new_password)}
    )
    db.commit()
    return True
