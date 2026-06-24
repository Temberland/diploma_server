from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from app.database import Base


class FixedExpense(Base):
    __tablename__ = "fixed_expenses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(255))
    sum = Column(Integer, nullable=True)
    date = Column(DateTime, nullable=True)
    repeat_type = Column(String(32), default="NONE")
    repeat_every_n_days = Column(Integer, nullable=True)
    is_paid = Column(Boolean, default=False)
    is_push_enabled = Column(Boolean, default=True)
    is_deleted = Column(Integer, default=0)
    version = Column(Integer, default=1)
