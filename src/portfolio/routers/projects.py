import os
import re
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from portfolio.database import get_db
from portfolio.model import Project
from portfolio.schema.project import ProjectOut, ProjectIn

router = APIRouter(prefix="/api/project", tags=["projects"])

WRITE_KEY = os.getenv("WRITE_KEY")


def make_slug(title: str) -> str:
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug


@router.get("", response_model=list[ProjectOut])
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project))
    return result.scalars().all()


@router.get("/{slug}", response_model=ProjectOut)
async def get_project(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.slug == slug))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ProjectOut)
async def create_project(payload: ProjectIn, db: AsyncSession = Depends(get_db)):
    if payload.writeKey != WRITE_KEY:
        raise HTTPException(status_code=403, detail="Invalid write key")

    new_project = Project(
        title=payload.title,
        slug=make_slug(payload.title),
        description=payload.description,
        tech_stack=payload.tech_stack,
        url=payload.url,
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int, writeKey: str, db: AsyncSession = Depends(get_db)
):
    if writeKey != WRITE_KEY:
        raise HTTPException(status_code=403, detail="Invalid write key")
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
    await db.commit()
    return {"deleted": project_id}


@router.put("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: int,
    payload: ProjectIn,
    db: AsyncSession = Depends(get_db),
    x_write_key: str | None = Header(default=None),
):
    provided = x_write_key or payload.writeKey
    if provided != WRITE_KEY:
        raise HTTPException(status_code=403, detail="Invalid write key")

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if payload.title and payload.title != project.title:
        setattr(project, "title", payload.title)
        setattr(project, "slug", make_slug(payload.title))
        setattr(project, "description", payload.description)
        setattr(project, "tech_stack", payload.tech_stack)
        setattr(project, "url", payload.url)

    await db.commit()
    await db.refresh(project)
    return project
