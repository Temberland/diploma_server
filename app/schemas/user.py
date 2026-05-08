from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    currency: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    currency: Optional[str]
    is_subscripted: bool
    is_active: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str
