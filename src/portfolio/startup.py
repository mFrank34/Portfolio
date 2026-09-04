from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from sqlalchemy import engine
from sqlalchemy import select

from portfolio.database import Base, async_session, engine
from portfolio.model.user import User
from portfolio.config import settings, PASSWORD_HASH


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        result = await db.execute(
            select(User).filter(User.username == settings.admin_username)
        )
        existing_user = result.scalars().first()

        if not existing_user:
            if len(settings.password) < 12:
                raise RuntimeError(
                    f"settings.password is too short ({len(settings.password)} chars, "
                    "minimum 12) — refusing to bootstrap admin user with a weak password. "
                    "Set a stronger PASSWORD in your .env before starting the app."
                )
            hashed_pw = PASSWORD_HASH.hash(settings.password)
            admin_user = User(
                username=settings.admin_username, hashed_password=hashed_pw
            )
            db.add(admin_user)
            await db.commit()
            print(f"Bootstrapped admin user '{settings.admin_username}'.")
        else:
            print(f"Admin user '{settings.admin_username}' already exists.")

    yield
