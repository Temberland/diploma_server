from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    currency: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError("Пароль должен быть не менее 6 символов")
        return v

    @field_validator("currency")
    @classmethod
    def currency_length(cls, v):
        if v is not None and len(v) != 1:
            raise ValueError("Валюта должна быть одним символом")
        return v


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
