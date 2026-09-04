from fastapi import APIRouter
from fastapi import Request, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi import Depends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import os

from portfolio.database import get_db, async_session
from portfolio.model.blog import Blog
from portfolio.model.project import Project
from portfolio.auth import get_current_user, get_token_from_cookie
from portfolio.shared.static_file import _serve_static_file
from portfolio.config import STATIC_DIR

router = APIRouter(tags=["Root"])


@router.get("/blog/{slug}")
async def blog_post_page(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Blog.id).where(Blog.slug == slug))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return _serve_static_file("blog.html")


@router.get("/project/{slug}")
async def project_page(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project.id).where(Project.slug == slug))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return _serve_static_file("project.html")


@router.get("/admin")
async def admin_page(request: Request):
    try:
        token = await get_token_from_cookie(request)
        async with async_session() as db:
            await get_current_user(token, db)
    except HTTPException:
        return RedirectResponse(url="/login")
    return _serve_static_file("editor.html")


@router.get("/favicon.ico")
async def get_icon():
    return _serve_static_file("assets/favicon.ico")


@router.get("/cv")
async def get_cv():
    return _serve_static_file("assets/cv.pdf")


@router.get("/{page_name}")
async def serve_page(page_name: str):
    file_path = os.path.abspath(os.path.join(STATIC_DIR, f"{page_name}.html"))
    static_root = os.path.abspath(STATIC_DIR)

    if not file_path.startswith(static_root + os.sep):
        raise HTTPException(status_code=404, detail="Page not found")

    if os.path.isfile(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Page not found")
