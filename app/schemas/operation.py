from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class OperationSync(BaseModel):
    id: int
    category_id: Optional[int] = None
    sum: str  # зашифрованное на сервере
    operation_type: Optional[str] = None
    account_id: Optional[int] = None
    date: Optional[datetime] = None
    description: Optional[str] = None
    is_deleted: int = 0
    version: int = 1


class AccountSync(BaseModel):
    id: int
    name: Optional[str] = None
    balance: str  # зашифрованное на сервере
    currency: Optional[str] = None
    account_type: Optional[str] = None


class CategorySync(BaseModel):
    id: int
    name: Optional[str] = None
    type: Optional[str] = None
    image_url: Optional[str] = None


class LimitSync(BaseModel):
    id: int
    category_id: Optional[int] = None
    sum: Optional[int] = None
    period: Optional[datetime] = None


class PatternSync(BaseModel):
    id: int
    name: Optional[str] = None
    sum: Optional[int] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None


class FixedExpenseSync(BaseModel):
    id: int
    name: Optional[str] = None
    sum: Optional[int] = None
    period: Optional[datetime] = None


class SyncUploadRequest(BaseModel):
    last_sync_at: Optional[datetime] = None  # для delta sync
    operations: List[OperationSync] = []
    accounts: List[AccountSync] = []
    categories: List[CategorySync] = []
    limits: List[LimitSync] = []
    patterns: List[PatternSync] = []
    fixed_expenses: List[FixedExpenseSync] = []


class SyncRestoreResponse(BaseModel):
    operations: List[OperationSync] = []
    accounts: List[AccountSync] = []
    categories: List[CategorySync] = []
    limits: List[LimitSync] = []
    patterns: List[PatternSync] = []
    fixed_expenses: List[FixedExpenseSync] = []
