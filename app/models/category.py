from sqlalchemy import Column, Integer, String
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    type = Column(String(255))
    icon_name = Column(String(255), default="")
    color_hex = Column(String(16), default="#FF6200EE")
    is_deleted = Column(Integer, default=0)
    version = Column(Integer, default=1)
