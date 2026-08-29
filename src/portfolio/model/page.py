from sqlalchemy import String, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime

from portfolio.database import Base, utcnow_naive


class Page(Base):
    __tablename__ = "page"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    hero_title: Mapped[str] = mapped_column(String(200))
    hero_subtitle: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=utcnow_naive)
    updated_at: Mapped[datetime] = mapped_column(
        default=utcnow_naive,
        onupdate=utcnow_naive,
    )

    __table_args__ = (CheckConstraint("id = 1", name="singleton_page"),)
