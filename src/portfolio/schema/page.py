from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PageOut(BaseModel):
    id: int
    hero_title: str
    hero_subtitle: str
    content: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PageIn(BaseModel):
    hero_title: str
    hero_subtitle: str
    content: str
