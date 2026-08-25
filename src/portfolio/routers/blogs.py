import hmac
import os
import re

import bleach
import markdown
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from portfolio.database import get_db
from portfolio.model import Blog
from portfolio.schema.blog import BlogIn, BlogOut

router = APIRouter(prefix="/api/blog", tags=["blog"])

try:
    WRITE_KEY: str = os.environ["WRITE_KEY"]
except KeyError as exc:
    raise RuntimeError("WRITE_KEY environment variable must be set") from exc

ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS.union(
    {"p", "pre", "h1", "h2", "h3", "h4", "img", "br", "hr", "span"}
)
ALLOWED_ATTRS = {**bleach.sanitizer.ALLOWED_ATTRIBUTES, "img": ["src", "alt", "title"]}


def make_slug(title: str) -> str:
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug or "post"


def render_html(content_md: str) -> str:
    raw_html = markdown.markdown(content_md)
    return bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)


def check_write_key(provided: str | None) -> None:
    if not provided or not hmac.compare_digest(provided, WRITE_KEY):
        raise HTTPException(status_code=403, detail="Invalid write key")


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


@router.post("", response_model=BlogOut)
async def create_post(payload: BlogIn, db: AsyncSession = Depends(get_db)):
    check_write_key(payload.writeKey)

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


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    x_write_key: str | None = Header(default=None),
):
    check_write_key(x_write_key)

    result = await db.execute(select(Blog).where(Blog.id == post_id))
    blog = result.scalar_one_or_none()
    if not blog:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.delete(blog)
    await db.commit()
    return {"deleted": post_id}
