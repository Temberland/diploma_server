from sqlalchemy import Column, Integer, String, Boolean, Date, Text
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    currency = Column(String(1))
    email = Column(String(255), unique=True, nullable=False)
    hash_password = Column(Text, nullable=False)
    is_subscripted = Column(Boolean, default=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
