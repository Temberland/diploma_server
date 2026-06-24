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
    currency: Optional[str] = "RUB"
    account_type: Optional[str] = None
    is_excluded_from_total: int = 0
    is_deleted: int = 0
    version: int = 1


class CategorySync(BaseModel):
    id: int
    name: Optional[str] = None
    type: Optional[str] = None
    icon_name: Optional[str] = ""
    color_hex: Optional[str] = "#FF6200EE"
    is_deleted: int = 0
    version: int = 1


class LimitSync(BaseModel):
    id: int
    category_id: Optional[int] = None
    sum: Optional[int] = None
    period: Optional[str] = None  # WEEK / MONTH / QUARTER / YEAR
    is_notification_enabled: int = 1
    is_deleted: int = 0
    version: int = 1


class PatternSync(BaseModel):
    id: int
    name: Optional[str] = None
    type: Optional[str] = None  # INCOME / EXPENSE / TRANSFER
    sum: Optional[int] = None
    account_id: Optional[int] = None
    category_id: Optional[int] = None
    note: Optional[str] = ""
    is_deleted: int = 0
    version: int = 1


class FixedExpenseSync(BaseModel):
    id: int
    name: Optional[str] = None
    sum: Optional[int] = None
    date: Optional[datetime] = None
    repeat_type: Optional[str] = "NONE"  # NONE / MONTHLY / EVERY_N_DAYS
    repeat_every_n_days: Optional[int] = None
    is_paid: bool = False
    is_push_enabled: bool = True
    is_deleted: int = 0
    version: int = 1


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
