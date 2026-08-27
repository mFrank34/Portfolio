from pydantic import BaseModel

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
    title: str
    description: str | None
    tech_stack: str | None
    url: str | None