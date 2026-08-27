from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime, timezone

from portfolio.database import Base


class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    level = Column(String(20))
