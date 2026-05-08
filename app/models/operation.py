from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from app.database import Base


class Operation(Base):
    __tablename__ = "operations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sum = Column(Text)  # зашифрованное
    operation_type = Column(String(255))
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    date = Column(DateTime, nullable=True)
    description = Column(String(255), nullable=True)
    is_deleted = Column(Integer, default=0)  # soft delete
    version = Column(Integer, default=1)  # для delta sync
