from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from portfolio.auth import get_current_user
from portfolio.database import get_db
from portfolio.model.social import Social
from portfolio.schema.social import SocialIn, SocialOut

router = APIRouter(prefix="/api/socials", tags=["Socials"])


@router.get("", response_model=list[SocialOut])
async def list_socials(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Social))
    return result.scalars().all()


@router.post("", response_model=SocialOut, dependencies=[Depends(get_current_user)])
async def create_social(payload: SocialIn, db: AsyncSession = Depends(get_db)):
    new_social = Social(site=payload.site, link=str(payload.link), icon=payload.icon)

    db.add(new_social)
    await db.commit()
    await db.refresh(new_social)
    return new_social


@router.put(
    "/{social_id}", response_model=SocialOut, dependencies=[Depends(get_current_user)]
)
async def update_social(
    social_id: int,
    payload: SocialIn,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Social).where(Social.id == social_id))
    social = result.scalar_one_or_none()
    if not social:
        raise HTTPException(status_code=404, detail="Social not found")

    social.site = payload.site  # pyright: ignore[reportAttributeAccessIssue]
    social.link = str(payload.link)  # pyright: ignore[reportAttributeAccessIssue]
    social.icon = payload.icon  # pyright: ignore[reportAttributeAccessIssue]

    await db.commit()
    await db.refresh(social)
    return social


@router.delete("/{social_id}", dependencies=[Depends(get_current_user)])
async def delete_social(social_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Social).where(Social.id == social_id))
    social = result.scalar_one_or_none()
    if not social:
        raise HTTPException(status_code=404, detail="Social not found")

    await db.delete(social)
    await db.commit()
    return {"deleted": social_id}
