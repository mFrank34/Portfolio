from pydantic import BaseModel


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
