import secrets
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.models.shared_account import SharedAccountMember, SharedAccountInvite
from app.models.account import Account


def is_member(account_id: int, user_id: int, db: Session) -> bool:
    """Проверяет, является ли пользователь участником совместного счёта."""
    return db.query(SharedAccountMember).filter(
        SharedAccountMember.account_id == account_id,
        SharedAccountMember.user_id == user_id
    ).first() is not None


def make_shared(account_id: int, owner_id: int, db: Session) -> SharedAccountMember:
    """
    Делает счёт совместным: добавляет владельца как первого участника.
    Если уже есть участники — просто возвращает существующую запись.
    """
    existing = db.query(SharedAccountMember).filter(
        SharedAccountMember.account_id == account_id,
        SharedAccountMember.user_id == owner_id
    ).first()
    if existing:
        return existing

    member = SharedAccountMember(account_id=account_id, user_id=owner_id)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def create_invite(
    account_id: int,
    created_by: int,
    db: Session,
    expires_hours: Optional[int] = 48
) -> SharedAccountInvite:
    """Создаёт пригласительный код для счёта."""
    code = secrets.token_urlsafe(16)
    expires_at = datetime.utcnow() + timedelta(hours=expires_hours) if expires_hours else None

    invite = SharedAccountInvite(
        account_id=account_id,
        invite_code=code,
        created_by=created_by,
        expires_at=expires_at,
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


def join_by_invite(invite_code: str, user_id: int, db: Session) -> SharedAccountMember:
    """
    Принимает приглашение по коду.
    Возвращает запись участника (новую или существующую).
    Бросает ValueError при невалидном/истёкшем коде.
    """
    invite = db.query(SharedAccountInvite).filter(
        SharedAccountInvite.invite_code == invite_code
    ).first()

    if not invite:
        raise ValueError("Приглашение не найдено")

    if invite.expires_at and invite.expires_at < datetime.utcnow():
        raise ValueError("Срок действия приглашения истёк")

    # Уже участник — идемпотентно
    existing = db.query(SharedAccountMember).filter(
        SharedAccountMember.account_id == invite.account_id,
        SharedAccountMember.user_id == user_id
    ).first()
    if existing:
        return existing

    member = SharedAccountMember(account_id=invite.account_id, user_id=user_id)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def leave_shared(account_id: int, user_id: int, db: Session) -> bool:
    """
    Выходит из совместного счёта.
    Возвращает True если запись удалена, False если пользователь не был участником.
    """
    member = db.query(SharedAccountMember).filter(
        SharedAccountMember.account_id == account_id,
        SharedAccountMember.user_id == user_id
    ).first()
    if not member:
        return False
    db.delete(member)
    db.commit()
    return True


def get_shared_account_ids(user_id: int, db: Session) -> list[int]:
    """Возвращает список account_id, где пользователь является участником совместного счёта."""
    rows = db.query(SharedAccountMember.account_id).filter(
        SharedAccountMember.user_id == user_id
    ).all()
    return [r.account_id for r in rows]


def get_members(account_id: int, db: Session) -> list[SharedAccountMember]:
    return db.query(SharedAccountMember).filter(
        SharedAccountMember.account_id == account_id
    ).all()
