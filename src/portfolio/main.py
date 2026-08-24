import os

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from portfolio.database import get_db, engine, Base
from portfolio.model import Project, Skill
from portfolio.schema import ProjectOut, SkillOut

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  
        
@app.get("/api/projects", response_model=list[ProjectOut])
async def get_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project))
    return result.scalars().all()

@app.get("/api/skills", response_model=list[SkillOut])
async def get_skills(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Skill))
    return result.scalars().all()

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")