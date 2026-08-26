import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from portfolio.auth import require_write_key
from portfolio.database import get_db
from portfolio.model import Project
from portfolio.schema.project import ProjectIn, ProjectOut

router = APIRouter(prefix="/api/project", tags=["projects"])


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


@router.post("", response_model=ProjectOut, dependencies=[Depends(require_write_key)])
async def create_project(payload: ProjectIn, db: AsyncSession = Depends(get_db)):
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


@router.put(
    "/{project_id}",
    response_model=ProjectOut,
    dependencies=[Depends(require_write_key)],
)
async def update_project(
    project_id: int, payload: ProjectIn, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.title = payload.title
    project.slug = make_slug(payload.title)
    project.description = payload.description
    project.tech_stack = payload.tech_stack
    project.url = payload.url

    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", dependencies=[Depends(require_write_key)])
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await db.delete(project)
    await db.commit()
    return {"deleted": project_id}
