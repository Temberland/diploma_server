from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SharedAccountCreate(BaseModel):
    account_id: int  # существующий счёт, который делаем совместным


class SharedAccountInviteResponse(BaseModel):
    invite_code: str
    account_id: int
    expires_at: Optional[datetime] = None


class SharedAccountJoin(BaseModel):
    invite_code: str


class SharedAccountMemberOut(BaseModel):
    user_id: int
    joined_at: datetime

    class Config:
        from_attributes = True


class SharedAccountOut(BaseModel):
    account_id: int
    members: list[SharedAccountMemberOut]
