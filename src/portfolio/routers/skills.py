import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from portfolio.database import get_db
from portfolio.model import Skill
from portfolio.schema import SkillOut, SkillIn

router = APIRouter(prefix="/api/skills", tags=["skills"])

WRITE_KEY = os.getenv("WRITE_KEY")

@router.get("", response_model=list[SkillOut])
async def list_skills(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Skill))
    return result.scalars().all()

@router.post("", response_model=SkillOut)
async def create_skill(payload: SkillIn, db: AsyncSession = Depends(get_db)):
    if payload.writeKey != WRITE_KEY:
        raise HTTPException(status_code=403, detail="Invalid write key")

    new_skill = Skill(
        name=payload.name,
        category=payload.category,
        level=payload.level,
    )
    db.add(new_skill)
    await db.commit()
    await db.refresh(new_skill)
    return new_skill

@router.delete("/{skill_id}")
async def delete_skill(skill_id: int, writeKey: str, db: AsyncSession = Depends(get_db)):
    if writeKey != WRITE_KEY:
        raise HTTPException(status_code=403, detail="Invalid write key")

    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    await db.delete(skill)
    await db.commit()
    return {"deleted": skill_id}