from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.database import Base


class FixedExpense(Base):
    __tablename__ = "fixed_expenses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(255))
    sum = Column(Integer)
    period = Column(DateTime, nullable=True)
