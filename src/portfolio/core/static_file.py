from http.client import HTTPException
import os

from fastapi.responses import FileResponse

from portfolio.config import STATIC_DIR


def _serve_static_file(filename: str) -> FileResponse:
    file_path = os.path.join(STATIC_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Page not found")
    return FileResponse(file_path)
