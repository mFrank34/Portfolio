from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class PageOut(BaseModel):
    id: int
    hero_title: str
    hero_subtitle: Optional[str] = None
    content_md: Optional[str] = None
    create_at: datetime

    class Config:
        from_attributes = True


class PageIn(BaseModel):
    id: int
    hero_title: str
    hero_subtitle: Optional[str] = None
    content_md: Optional[str] = None
    create_at: datetime
