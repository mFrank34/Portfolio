from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime, timezone

from portfolio.database import Base


class Social(Base):
    __tablename__ = "socials"
    id = Column(Integer, primary_key=True)
    site = Column(String, nullable=False)
    link = Column(String, nullable=False)
    icon = Column(String, nullable=False)
