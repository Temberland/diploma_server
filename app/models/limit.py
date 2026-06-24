from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class Limit(Base):
    __tablename__ = "limits"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sum = Column(Integer)
    period = Column(String(16), nullable=True)  # WEEK / MONTH / QUARTER / YEAR
    is_notification_enabled = Column(Integer, default=1)
    is_deleted = Column(Integer, default=0)
    version = Column(Integer, default=1)
