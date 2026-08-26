from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from portfolio.auth import require_write_key
from portfolio.database import get_db
from portfolio.model import Skill
from portfolio.schema.skill import SkillIn, SkillOut

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("", response_model=list[SkillOut])
async def list_skills(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Skill))
    return result.scalars().all()


@router.post("", response_model=SkillOut, dependencies=[Depends(require_write_key)])
async def create_skill(payload: SkillIn, db: AsyncSession = Depends(get_db)):
    new_skill = Skill(
        name=payload.name,
        category=payload.category,
        level=payload.level,
    )

    db.add(new_skill)
    await db.commit()
    await db.refresh(new_skill)
    return new_skill


@router.put("/{skill_id}", response_class=SkillOut, dependencies=[Depends(get_db)])
async def update_skill(
    skill_id: int, payload, skillIn, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    if payload.name and payload.name != skill.name:
        setattr(skill, "name", payload.name)
        setattr(skill, "category", payload.category)
        setattr(skill, "level", payload.level)

    await db.commit()
    await db.refresh(Skill)
    return skill


@router.delete("/{skill_id}", dependencies=[Depends(require_write_key)])
async def delete_skill(skill_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    await db.delete(skill)
    await db.commit()
    return {"deleted": skill_id}
