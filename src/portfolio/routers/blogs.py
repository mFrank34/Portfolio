import os
import re
import markdown
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from portfolio.database import get_db
from portfolio.model import Post
from portfolio.schema import PostOut, PostIn

router = APIRouter(prefix="/api/blog", tags=["blog"])

WRITE_KEY = os.getenv("WRITE_KEY")


def make_slug(title: str) -> str:
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug


@router.get("", response_model=list[PostOut])
async def list_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).order_by(Post.created_at.desc()))
    posts = result.scalars().all()
    return [
        PostOut(
            id=p.id, title=p.title, slug=p.slug,
            content_html=markdown.markdown(p.content_md),
            created_at=p.created_at,
        )
        for p in posts
    ]


@router.get("/{slug}", response_model=PostOut)
async def get_post(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.slug == slug))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostOut(
        id=post.id, title=post.title, slug=post.slug,
        content_html=markdown.markdown(post.content_md),
        created_at=post.created_at,
    )


@router.post("", response_model=PostOut)
async def create_post(payload: PostIn, db: AsyncSession = Depends(get_db)):
    if payload.writeKey != WRITE_KEY:
        raise HTTPException(status_code=403, detail="Invalid write key")

    new_post = Post(
        title=payload.title,
        slug=make_slug(payload.title),
        content_md=payload.content_md,
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    return PostOut(
        id=new_post.id, title=new_post.title, slug=new_post.slug,
        content_html=markdown.markdown(new_post.content_md),
        created_at=new_post.created_at,
    )


@router.delete("/{post_id}")
async def delete_post(post_id: int, writeKey: str, db: AsyncSession = Depends(get_db)):
    if writeKey != WRITE_KEY:
        raise HTTPException(status_code=403, detail="Invalid write key")

    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.delete(post)
    await db.commit()
    return {"deleted": post_id}