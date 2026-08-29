import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pwdlib import PasswordHash
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import select

from portfolio.config import settings
from portfolio.database import Base, async_session, engine
from portfolio.limiter import limiter
from portfolio.model.user import User
from portfolio.routers import auth, blogs, page, projects, skills, socials

password_hash = PasswordHash.recommended()
STATIC_DIR = os.path.join(os.path.dirname(__file__), "../static")


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
            hashed_pw = password_hash.hash(settings.password)
            admin_user = User(
                username=settings.admin_username, hashed_password=hashed_pw
            )
            db.add(admin_user)
            await db.commit()
            print(f"Bootstrapped admin user '{settings.admin_username}'.")
        else:
            print(f"Admin user '{settings.admin_username}' already exists.")

    yield


app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(page.router)
app.include_router(socials.router)
app.include_router(skills.router)
app.include_router(projects.router)
app.include_router(blogs.router)
app.include_router(auth.router)


def _serve_static_file(filename: str) -> FileResponse:
    file_path = os.path.join(STATIC_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Page not found")
    return FileResponse(file_path)


@app.get("/blog/{slug}")
async def blog_post_page():
    return _serve_static_file("blog.html")


@app.get("/project/{project_id}")
async def project_page():
    return _serve_static_file("project.html")


@app.get("/admin")
async def admin_page():
    return _serve_static_file("editor.html")


@app.get("/favicon.ico")
async def get_icon():
    return _serve_static_file("assets/favicon.ico")


@app.get("/cv")
async def get_cv():
    return _serve_static_file("assets/cv.pdf")


@app.get("/{page_name}")
async def serve_page(page_name: str):
    file_path = os.path.abspath(os.path.join(STATIC_DIR, f"{page_name}.html"))
    static_root = os.path.abspath(STATIC_DIR)

    if not file_path.startswith(static_root + os.sep):
        raise HTTPException(status_code=404, detail="Page not found")

    if os.path.isfile(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Page not found")


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
