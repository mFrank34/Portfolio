import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from portfolio.database import engine, Base
from portfolio.routers import projects, skills, blog

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(projects.router)
app.include_router(skills.router)
app.include_router(blog.router)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")