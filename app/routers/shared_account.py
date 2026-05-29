from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.account import Account
from app.schemas.shared_account import (
    SharedAccountCreate, SharedAccountInviteResponse,
    SharedAccountJoin, SharedAccountOut, SharedAccountMemberOut
)
from app.services.shared_account import (
    make_shared, create_invite, join_by_invite,
    leave_shared, get_members, is_member
)

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=SharedAccountInviteResponse)
def create_shared_account(
    data: SharedAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Делает существующий счёт совместным и возвращает пригласительный код.
    Счёт должен принадлежать текущему пользователю.
    """
    account = db.query(Account).filter(
        Account.id == data.account_id,
        Account.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Счёт не найден или не принадлежит вам")

    make_shared(data.account_id, current_user.id, db)
    invite = create_invite(data.account_id, current_user.id, db)

    return SharedAccountInviteResponse(
        invite_code=invite.invite_code,
        account_id=invite.account_id,
        expires_at=invite.expires_at,
    )


@router.post("/invite/{account_id}", response_model=SharedAccountInviteResponse)
def generate_invite(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Генерирует новый пригласительный код для уже совместного счёта."""
    if not is_member(account_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Вы не участник этого счёта")

    invite = create_invite(account_id, current_user.id, db)
    return SharedAccountInviteResponse(
        invite_code=invite.invite_code,
        account_id=invite.account_id,
        expires_at=invite.expires_at,
    )


@router.post("/join", status_code=status.HTTP_200_OK)
def join_shared_account(
    data: SharedAccountJoin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Вступает в совместный счёт по пригласительному коду."""
    try:
        member = join_by_invite(data.invite_code, current_user.id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"detail": "Вы добавлены к совместному счёту", "account_id": member.account_id}


@router.delete("/leave/{account_id}", status_code=status.HTTP_200_OK)
def leave_shared_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Выходит из совместного счёта."""
    removed = leave_shared(account_id, current_user.id, db)
    if not removed:
        raise HTTPException(status_code=404, detail="Вы не являетесь участником этого счёта")
    return {"detail": "Вы вышли из совместного счёта"}


@router.get("/{account_id}/members", response_model=SharedAccountOut)
def get_shared_members(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Возвращает список участников совместного счёта."""
    if not is_member(account_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Вы не участник этого счёта")

    members = get_members(account_id, db)
    return SharedAccountOut(
        account_id=account_id,
        members=[SharedAccountMemberOut(user_id=m.user_id, joined_at=m.joined_at) for m in members]
    )
