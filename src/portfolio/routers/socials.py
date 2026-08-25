import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from portfolio.database import get_db
from portfolio.model import Social
from portfolio.schema.social import SocialOut, SocialIn

router = APIRouter(prefix="api/socials", tags=["socials"])

WRITE_KEY = os.getenv("WRITE_KEY")


@router.get("", response_model=list[SocialOut])
async def list_socials(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Social))
    return result.scalars().all()


@router.post("", response_model=SocialOut)
async def create_social(payload: SocialIn, db: AsyncSession = Depends(get_db)):
    if payload.writeKey != WRITE_KEY:
        raise HTTPException(status_code=403, detail="Invalid write key")

    new_social = Social(site=payload.site, link=payload.link)

    db.add(new_social)
    await db.commit()
    await db.refresh(new_social)
    return new_social


@router.delete("/{social_id}")
async def delete_social(
    social_id: int, writeKey: str, db: AsyncSession = Depends(get_db)
):
    if writeKey != WRITE_KEY:
        raise HTTPException(status_code=403, detail="Invalid write key")

    result = await db.execute(select(Social).where(Social.id == social_id))
    social = result.scalar_one_or_none()
    if not social:
        raise HTTPException(status_code=404, detail="Social not found")

    await db.delete(social)
    await db.commit()
    return {"deleted": social_id}
