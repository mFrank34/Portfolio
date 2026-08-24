from sqlalchemy import Column, Integer, String, Text
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
    category = Column(String(50))  # e.g. "language", "framework", "tool"
    level = Column(String(20))     # e.g. "beginner", "intermediate", "advanced"