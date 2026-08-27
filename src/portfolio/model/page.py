from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime, timezone

from portfolio.database import Base


class Page(Base):
    __tablename__ = "page"

    id: Mapped[int] = mapped_column(primary_key=True)
    hero_title: Mapped[str] = mapped_column(String(200))
    hero_subtitle: Mapped[str] = mapped_column(String(200))
    content_md: Mapped[str] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
