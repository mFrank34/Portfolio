from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime, timezone

from .database import Base


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    tech_stack = Column(String(200))
    url = Column(String(200))


class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    level = Column(String(20))


class Social(Base):
    __tablename__ = "socials"
    id = Column(Integer, primary_key=True)
    site = Column(String, nullable=False)
    link = Column(String, nullable=False)
    icon = Column(String, nullable=False)


class Blog(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200), unique=True)
    content_md: Mapped[str] = mapped_column(Text)  # raw markdown, as written
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
