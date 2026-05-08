from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(255))
    balance = Column(Text)  # зашифрованное
    currency = Column(String(1))
    account_type = Column(String(255))
