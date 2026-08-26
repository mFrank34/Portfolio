import secrets
from fastapi import Header, HTTPException
from .config import settings


def require_key(incoming_write_key: str = Header(default="")):
    if not secrets.compare_digest(incoming_write_key, settings.write_key):
        raise HTTPException(status_code=401, detail="Invalid write key")
