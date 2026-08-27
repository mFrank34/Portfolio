from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime, timezone

from portfolio.database import Base


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    tech_stack = Column(String(200))
    url = Column(String(200))
