from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from portfolio.auth import require_key
from portfolio.database import get_db
from portfolio.model.blog import Blog
from portfolio.schema.blog import BlogIn, BlogOut
from portfolio.shared.slug import make_slug
from portfolio.shared.render import render_html

router = APIRouter(prefix="/api/blog", tags=["blog"])


async def get_unique_slug(db: AsyncSession, base_slug: str) -> str:
    slug = base_slug
    suffix = 1
    while True:
        result = await db.execute(select(Blog.id).where(Blog.slug == slug))
        if result.scalar_one_or_none() is None:
            return slug
        suffix += 1
        slug = f"{base_slug}-{suffix}"


@router.get("", response_model=list[BlogOut])
async def list_posts(
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
):
    limit = max(1, min(limit, 100))
    result = await db.execute(
        select(Blog).order_by(Blog.created_at.desc()).limit(limit).offset(offset)
    )
    posts = result.scalars().all()
    return [
        BlogOut(
            id=p.id,
            title=p.title,
            slug=p.slug,
            content_html=render_html(p.content_md),
            created_at=p.created_at,
        )
        for p in posts
    ]


@router.get("/{post_id}/raw", dependencies=[Depends(require_key)])
async def get_post_raw(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Blog).where(Blog.id == post_id))
    blog = result.scalar_one_or_none()
    if not blog:
        raise HTTPException(status_code=404, detail="Post not found")
    return {
        "id": blog.id,
        "title": blog.title,
        "slug": blog.slug,
        "content_md": blog.content_md,
    }


@router.get("/{slug}", response_model=BlogOut)
async def get_post(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Blog).where(Blog.slug == slug))
    blog = result.scalar_one_or_none()
    if not blog:
        raise HTTPException(status_code=404, detail="Post not found")
    return BlogOut(
        id=blog.id,
        title=blog.title,
        slug=blog.slug,
        content_html=render_html(blog.content_md),
        created_at=blog.created_at,
    )


@router.post("", response_model=BlogOut, dependencies=[Depends(require_key)])
async def create_post(payload: BlogIn, db: AsyncSession = Depends(get_db)):
    base_slug = make_slug(payload.title)
    slug = await get_unique_slug(db, base_slug)

    new_blog = Blog(
        title=payload.title,
        slug=slug,
        content_md=payload.content_md,
    )
    db.add(new_blog)
    await db.commit()
    await db.refresh(new_blog)

    return BlogOut(
        id=new_blog.id,
        title=new_blog.title,
        slug=new_blog.slug,
        content_html=render_html(new_blog.content_md),
        created_at=new_blog.created_at,
    )


@router.delete("/{post_id}", dependencies=[Depends(require_key)])
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Blog).where(Blog.id == post_id))
    blog = result.scalar_one_or_none()
    if not blog:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.delete(blog)
    await db.commit()
    return {"deleted": post_id}


@router.put("/{post_id}", response_model=BlogOut, dependencies=[Depends(require_key)])
async def update_blog(
    post_id: int, payload: BlogIn, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Blog).where(Blog.id == post_id))
    blog = result.scalar_one_or_none()
    if not blog:
        raise HTTPException(status_code=404, detail="Post not found")

    # Update title and content; if title changed, compute a new unique slug
    if payload.title and payload.title != blog.title:
        base_slug = make_slug(payload.title)
        slug = await get_unique_slug(db, base_slug)
        blog.slug = slug
        blog.title = payload.title
    if payload.content_md is not None:
        blog.content_md = payload.content_md

    await db.commit()
    await db.refresh(blog)

    return BlogOut(
        id=blog.id,
        title=blog.title,
        slug=blog.slug,
        content_html=render_html(blog.content_md),
        created_at=blog.created_at,
    )
