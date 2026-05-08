from sqlalchemy import Column, Integer, Text, DateTime
from datetime import datetime
from app.database import Base


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True)
    token = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
