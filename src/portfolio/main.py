import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from portfolio.database import engine, Base
from portfolio.routers import blogs, projects, skills

app = FastAPI()
STATIC_DIR = os.path.join(os.path.dirname(__file__), "../static")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(projects.router)
app.include_router(skills.router)
app.include_router(blogs.router)


@app.get("/blog/{slug}")
async def blog_post_page():
    return FileResponse(os.path.join(STATIC_DIR, "blog.html"))


@app.get("/project/{project_id}")
async def project_page():
    return FileResponse(os.path.join(STATIC_DIR, "project.html"))


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
