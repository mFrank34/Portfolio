from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime

from portfolio.database import Base, utcnow_naive


class Blog(Base):
    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200), unique=True)
    content_md: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=utcnow_naive)
    updated_at: Mapped[datetime] = mapped_column(
        default=utcnow_naive,
        onupdate=utcnow_naive,
    )
