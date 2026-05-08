from sqlalchemy import Column, Integer, ForeignKey, DateTime
from app.database import Base


class Limit(Base):
    __tablename__ = "limits"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sum = Column(Integer)
    period = Column(DateTime, nullable=True)
