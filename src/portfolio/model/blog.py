from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime, timezone

from portfolio.database import Base


class Blog(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200), unique=True)
    content_md: Mapped[str] = mapped_column(Text)  # raw markdown, as written
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
