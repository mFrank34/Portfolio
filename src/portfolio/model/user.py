from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String


from datetime import datetime, timezone

from portfolio.database import Base


class User(Base):
    __tablename__ = "admin_user"

    id = Column(Integer, primary_key=True)
    username = Column(String(256), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
