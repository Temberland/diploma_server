from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database import Base


class Pattern(Base):
    __tablename__ = "patterns"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    sum = Column(Integer)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    image_url = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
