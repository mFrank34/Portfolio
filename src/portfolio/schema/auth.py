from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    id: int
    username: str


class UserInDB(User):
    hashed_password: str


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str
