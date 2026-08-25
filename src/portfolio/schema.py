from pydantic import BaseModel
from datetime import datetime, timezone


class SkillOut(BaseModel):
    id: int
    name: str
    category: str | None
    level: str | None

    class Config:
        from_attributes = True


class SkillIn(BaseModel):
    writeKey: str
    name: str
    category: str | None
    level: str | None


class SocialIn(BaseModel):
    writeKey: str
    site: str
    link: str


class SocialOut(BaseModel):
    id: int
    site: str
    link: str

    class Config:
        from_attributes = True


class ProjectOut(BaseModel):
    id: int
    title: str
    slug: str
    description: str | None
    tech_stack: str | None
    url: str | None

    class Config:
        from_attributes = True


class ProjectIn(BaseModel):
    writeKey: str
    title: str
    description: str | None
    tech_stack: str | None
    url: str | None


class PostOut(BaseModel):
    id: int
    title: str
    slug: str
    content_html: str
    created_at: datetime

    class Config:
        from_attributes = True


class PostIn(BaseModel):
    writeKey: str
    title: str
    content_md: str
