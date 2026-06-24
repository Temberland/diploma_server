from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(255))
    balance = Column(Text)  # зашифрованное
    currency = Column(String(8), default="RUB")
    account_type = Column(String(255))
    is_excluded_from_total = Column(Integer, default=0)
    is_deleted = Column(Integer, default=0)
    version = Column(Integer, default=1)
