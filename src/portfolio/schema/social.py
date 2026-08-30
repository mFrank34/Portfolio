from pydantic import BaseModel, HttpUrl


class SocialIn(BaseModel):
    site: str
    link: HttpUrl
    icon: str


class SocialOut(BaseModel):
    id: int
    site: str
    link: HttpUrl
    icon: str

    class Config:
        from_attributes = True
