from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from portfolio.auth import require_key
from portfolio.database import get_db
from portfolio.model.page import Page
from portfolio.schema.page import PageIn, PageOut
from portfolio.shared.slug import make_slug
from portfolio.shared.render import render_html

router = APIRouter(prefix="/api/page", tags=["Page"])

