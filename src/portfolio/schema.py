from pydantic import BaseModel

class ProjectOut(BaseModel):
    id: int
    title: str
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
        
