from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from portfolio.core.static_file import _serve_static_file


async def not_found_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=404, content={"detail": exc.detail})
    return _serve_static_file("404.html")
