import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pwdlib import PasswordHash
from sqlalchemy import select

from portfolio.database import engine, Base, async_session
from portfolio.model.user import User
from portfolio.config import settings
from portfolio.routers import blogs, projects, skills, socials, page, auth

password_hash = PasswordHash.recommended()
STATIC_DIR = os.path.join(os.path.dirname(__file__), "../static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Seed default admin user from environment variables
    async with async_session() as db:
        result = await db.execute(
            select(User).filter(User.username == settings.admin_username)
        )
        existing_user = result.scalars().first()

        if not existing_user:
            hashed_pw = password_hash.hash(settings.password)
            admin_user = User(username=settings.admin_username, hashed_password=hashed_pw)
            db.add(admin_user)
            await db.commit()
            print(f"Bootstrapped admin user '{settings.admin_username}'.")
        else:
            print(f"Admin user '{settings.admin_username}' already exists.")
            
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(page.router)
app.include_router(socials.router)
app.include_router(skills.router)
app.include_router(projects.router)
app.include_router(blogs.router)
app.include_router(auth.router)


@app.get("/blog/{slug}")
async def blog_post_page():
    return FileResponse(os.path.join(STATIC_DIR, "blog.html"))


@app.get("/project/{project_id}")
async def project_page():
    return FileResponse(os.path.join(STATIC_DIR, "project.html"))

@app.get("/admin")
async def admin_page():
    return FileResponse(os.path.join(STATIC_DIR, "editor.html"))

@app.get("/favicon.ico")
async def get_icon():
    return FileResponse(os.path.join(STATIC_DIR, "assets/favicon.ico"))


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")