from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class Pattern(Base):
    __tablename__ = "patterns"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(255))
    type = Column(String(255), nullable=True)
    sum = Column(Integer)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    note = Column(String(255), default="")
    is_deleted = Column(Integer, default=0)
    version = Column(Integer, default=1)
