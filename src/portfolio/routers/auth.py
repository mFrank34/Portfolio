from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from portfolio.auth import authenticate_user, create_access_token, get_current_user
from portfolio.config import ACCESS_TOKEN_EXPIRE_MINUTES
from portfolio.database import get_db
from portfolio.model.user import User
from portfolio.schema.auth import UserOut
from portfolio.limiter import limiter
from portfolio.config import settings

from fastapi import Response, status, HTTPException, Depends

from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token")
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,  # <-- add this
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Set the token in a secure HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=settings.environment == "production",
        samesite="strict",
        max_age=int(access_token_expires.total_seconds()),
    )

    return {"message": "Login successful"}


@router.get("/me/", response_model=UserOut)
async def read_users_me(current_user: Annotated[UserOut, Depends(get_current_user)]):
    return current_user


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}
