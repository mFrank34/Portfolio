# syntax=docker/dockerfile:1

FROM python:3.14-slim AS base

# Install uv (copy the static binary, no extra deps needed)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# --- Install dependencies first (cached layer, separate from app code) ---
# Only copy lockfile + project metadata so this layer stays cached
# as long as dependencies don't change.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# --- Copy the rest of the app and install it ---
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Put the venv's bin dir on PATH so "python"/"uvicorn" resolve correctly
ENV PATH="/app/.venv/bin:$PATH"

# Run as non-root
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# src-layout project: app lives at src/portfolio/main.py
CMD ["uvicorn", "portfolio.main:app", "--host", "0.0.0.0", "--port", "8000"]