from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from portfolio.config import settings, STATIC_DIR
from portfolio.core.headers import SecurityHeadersMiddleware
from portfolio.database import async_session, get_db
from portfolio.core.limiter import limiter
from portfolio.routers import auth, blogs, page, projects, skills, socials, root
from portfolio.startup import lifespan
from portfolio.core.not_found import not_found_handler

app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(404, not_found_handler)

app.include_router(page.router)
app.include_router(socials.router)
app.include_router(skills.router)
app.include_router(projects.router)
app.include_router(blogs.router)
app.include_router(auth.router)
app.include_router(root.router)

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
