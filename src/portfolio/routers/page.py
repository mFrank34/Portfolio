from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from portfolio.auth import require_key
from portfolio.database import get_db
from portfolio.model.page import Page
from portfolio.schema.page import PageIn, PageOut
from portfolio.shared.render import render_html

router = APIRouter(prefix="/api/page", tags=["Page"])


@router.get("", response_model=PageOut)
async def get_page(db: AsyncSession = Depends(get_db)):
    page = await db.get(Page, 1)
    if page is None:
        raise HTTPException(status_code=404, detail="Page not found")

    return PageOut(
        id=page.id,
        hero_title=page.hero_title,
        hero_subtitle=page.hero_subtitle,
        content=render_html(page.content_md),
        created_at=page.created_at,
        updated_at=page.updated_at,
    )


@router.get("/raw", response_model=PageOut)
async def get_page_raw(db: AsyncSession = Depends(get_db)):
    page = await db.get(Page, 1)
    if page is None:
        raise HTTPException(status_code=404, detail="Page not found")

    return PageOut(
        id=page.id,
        hero_title=page.hero_title,
        hero_subtitle=page.hero_subtitle,
        content=page.content_md,
        created_at=page.created_at,
        updated_at=page.updated_at,
    )


@router.post("", response_model=PageOut, dependencies=[Depends(require_key)])
async def create_page(payload: PageIn, db: AsyncSession = Depends(get_db)):
    existing = await db.get(Page, 1)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Page already exists")

    page = Page(
        id=1,
        hero_title=payload.hero_title,
        hero_subtitle=payload.hero_subtitle,
        content_md=payload.content_md,
    )
    db.add(page)
    await db.commit()
    await db.refresh(page)

    return PageOut(
        id=page.id,
        hero_title=page.hero_title,
        hero_subtitle=page.hero_subtitle,
        content=render_html(page.content_md),
        created_at=page.created_at,
        updated_at=page.updated_at,
    )


@router.put("", response_model=PageOut, dependencies=[Depends(require_key)])
async def update_page(payload: PageIn, db: AsyncSession = Depends(get_db)):
    page = await db.get(Page, 1)
    if page is None:
        raise HTTPException(status_code=404, detail="Page not found")

    page.hero_title = payload.hero_title
    page.hero_subtitle = payload.hero_subtitle
    page.content_md = payload.content_md

    await db.commit()
    await db.refresh(page)

    return PageOut(
        id=page.id,
        hero_title=page.hero_title,
        hero_subtitle=page.hero_subtitle,
        content=render_html(page.content_md),
        created_at=page.created_at,
        updated_at=page.updated_at,
    )
