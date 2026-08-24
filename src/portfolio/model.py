from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone

from .database import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    tech_stack = Column(String(200))
    url = Column(String(200))

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    level = Column(String(20))
    
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    content_md = Column(Text, nullable=False)       # raw markdown, as written
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))