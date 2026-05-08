from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.models.operation import Operation
from app.models.account import Account
from app.models.category import Category
from app.models.limit import Limit
from app.models.pattern import Pattern
from app.models.fixed_expense import FixedExpense
from app.schemas.operation import (
    SyncUploadRequest, SyncRestoreResponse,
    OperationSync, AccountSync, CategorySync,
    LimitSync, PatternSync, FixedExpenseSync
)
from app.services.encryption import encrypt, decrypt


def sync_upload(user_id: int, data: SyncUploadRequest, db: Session):
    _sync_operations(user_id, data.operations, data.last_sync_at, db)
    _sync_accounts(user_id, data.accounts, data.last_sync_at, db)
    _sync_categories(data.categories, db)
    _sync_limits(user_id, data.limits, db)
    _sync_patterns(user_id, data.patterns, db)
    _sync_fixed_expenses(user_id, data.fixed_expenses, db)
    db.commit()


def sync_restore(user_id: int, db: Session) -> SyncRestoreResponse:
    operations = db.query(Operation).filter(Operation.user_id == user_id, Operation.is_deleted == 0).all()
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    categories = db.query(Category).all()
    limits = db.query(Limit).filter(Limit.user_id == user_id).all()
    patterns = db.query(Pattern).filter(Pattern.user_id == user_id).all()
    fixed_expenses = db.query(FixedExpense).filter(FixedExpense.user_id == user_id).all()

    return SyncRestoreResponse(
        operations=[OperationSync(
            id=o.id, category_id=o.category_id,
            sum=decrypt(o.sum), operation_type=o.operation_type,
            account_id=o.account_id, date=o.date,
            description=o.description, is_deleted=o.is_deleted, version=o.version
        ) for o in operations],
        accounts=[AccountSync(
            id=a.id, name=a.name,
            balance=decrypt(a.balance), currency=a.currency,
            account_type=a.account_type
        ) for a in accounts],
        categories=[CategorySync(
            id=c.id, name=c.name, type=c.type, image_url=c.image_url
        ) for c in categories],
        limits=[LimitSync(
            id=l.id, category_id=l.category_id, sum=l.sum, period=l.period
        ) for l in limits],
        patterns=[PatternSync(
            id=p.id, name=p.name, sum=p.sum,
            category_id=p.category_id, image_url=p.image_url
        ) for p in patterns],
        fixed_expenses=[FixedExpenseSync(
            id=f.id, name=f.name, sum=f.sum, period=f.period
        ) for f in fixed_expenses],
    )


# --- Вспомогательные функции ---

def _sync_operations(user_id: int, items: List[OperationSync], last_sync_at: Optional[datetime], db: Session):
    for item in items:
        existing = db.query(Operation).filter(
            Operation.id == item.id, Operation.user_id == user_id
        ).first()

        if existing:
            # Разрешение конфликтов: last write wins по version
            if item.version >= existing.version:
                existing.sum = encrypt(item.sum)
                existing.operation_type = item.operation_type
                existing.account_id = item.account_id
                existing.date = item.date
                existing.description = item.description
                existing.is_deleted = item.is_deleted
                existing.version = item.version + 1
        else:
            db.add(Operation(
                id=item.id, user_id=user_id,
                category_id=item.category_id,
                sum=encrypt(item.sum),
                operation_type=item.operation_type,
                account_id=item.account_id,
                date=item.date,
                description=item.description,
                is_deleted=item.is_deleted,
                version=item.version,
            ))


def _sync_accounts(user_id: int, items: List[AccountSync], last_sync_at: Optional[datetime], db: Session):
    for item in items:
        existing = db.query(Account).filter(
            Account.id == item.id, Account.user_id == user_id
        ).first()

        if existing:
            existing.name = item.name
            existing.balance = encrypt(item.balance)
            existing.currency = item.currency
            existing.account_type = item.account_type
        else:
            db.add(Account(
                id=item.id, user_id=user_id,
                name=item.name,
                balance=encrypt(item.balance),
                currency=item.currency,
                account_type=item.account_type,
            ))


def _sync_categories(items: List[CategorySync], db: Session):
    for item in items:
        existing = db.query(Category).filter(Category.id == item.id).first()
        if existing:
            existing.name = item.name
            existing.type = item.type
            existing.image_url = item.image_url
        else:
            db.add(Category(
                id=item.id, name=item.name,
                type=item.type, image_url=item.image_url
            ))


def _sync_limits(user_id: int, items: List[LimitSync], db: Session):
    for item in items:
        existing = db.query(Limit).filter(
            Limit.id == item.id, Limit.user_id == user_id
        ).first()
        if existing:
            existing.category_id = item.category_id
            existing.sum = item.sum
            existing.period = item.period
        else:
            db.add(Limit(
                id=item.id, user_id=user_id,
                category_id=item.category_id,
                sum=item.sum, period=item.period
            ))


def _sync_patterns(user_id: int, items: List[PatternSync], db: Session):
    for item in items:
        existing = db.query(Pattern).filter(
            Pattern.id == item.id, Pattern.user_id == user_id
        ).first()
        if existing:
            existing.name = item.name
            existing.sum = item.sum
            existing.category_id = item.category_id
            existing.image_url = item.image_url
        else:
            db.add(Pattern(
                id=item.id, user_id=user_id,
                name=item.name, sum=item.sum,
                category_id=item.category_id,
                image_url=item.image_url
            ))


def _sync_fixed_expenses(user_id: int, items: List[FixedExpenseSync], db: Session):
    for item in items:
        existing = db.query(FixedExpense).filter(
            FixedExpense.id == item.id, FixedExpense.user_id == user_id
        ).first()
        if existing:
            existing.name = item.name
            existing.sum = item.sum
            existing.period = item.period
        else:
            db.add(FixedExpense(
                id=item.id, user_id=user_id,
                name=item.name, sum=item.sum,
                period=item.period
            ))
