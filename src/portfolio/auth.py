import secrets
from typing import Annotated

from fastapi import Header, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from pwdlib import PasswordHash

from portfolio.model.user import User
from portfolio.config import settings

from .config import settings

password_hash = PasswordHash.recommended()
HASH_CODE = password_hash.hash(settings.secret_key)


def require_key(incoming_key: str = Header(default="", alias="X-Write-Key")):
    if not secrets.compare_digest(incoming_key, settings.write_key):
        raise HTTPException(status_code=401, detail="Invalid write key")


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def get_user(db: Session, username: str):
    return db.qurey(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        verify_password(password, HASH_CODE)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: Annotated[str, Depends(OAuth2PasswordBearer.oauth2_scheme)]):
    pass
