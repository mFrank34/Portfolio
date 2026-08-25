from pydantic import BaseModel


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
