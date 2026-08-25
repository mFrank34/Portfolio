from pydantic import BaseModel
from datetime import datetime


class BlogOut(BaseModel):
    id: int
    title: str
    slug: str
    content_html: str
    created_at: datetime

    class Config:
        from_attributes = True


class BlogIn(BaseModel):
    writeKey: str
    title: str
    content_md: str
