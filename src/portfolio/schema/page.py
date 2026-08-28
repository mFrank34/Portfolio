from datetime import datetime
from pydantic import BaseModel


class PageOut(BaseModel):
    id: int
    hero_title: str
    hero_subtitle: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PageIn(BaseModel):
    hero_title: str
    hero_subtitle: str
    content_md: str
