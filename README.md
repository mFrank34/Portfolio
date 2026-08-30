# Portfolio

A small personal portfolio backend and static site built with FastAPI and SQLAlchemy (async). This project serves a static frontend (in src/static) and exposes a JSON API for managing projects, skills and blog posts. It uses an async SQLAlchemy engine with a configurable database URL and a simple write-key based protection for mutating operations.

Come Checkout the Live Version ![Link](https://www.frankslab.uk/)

## Key features

- FastAPI application serving static pages and a JSON API
- Async SQLAlchemy models and async session management
- Simple content APIs for Projects, Skills and Blog posts
- Markdown-to-sanitized-HTML rendering for blog content
- Static frontend assets in src/static (index.html, blog.html, project.html)

#### Tech stack

- Python (see Requirements)
- FastAPI
- SQLAlchemy (async)
- aiosqlite (default SQLite async driver)
- Uvicorn for running the ASGI server

#### Requirements

- Python 3.14+ (as declared in pyproject.toml)
- Install dependencies from pyproject or requirements.txt

### Documation
on api can be found at <http://localhost:8000/docs>

# Contributing

Contributions are welcome. Please open issues or pull requests with clear descriptions of changes. For code changes, prefer small, focused PRs.

# Troubleshooting

- If you see RuntimeError: DATABASE_URL environment variable is not set — set DATABASE_URL either in the environment or in src/portfolio/.env and restart the server.
- If write operations are rejected with 403, ensure WRITE_KEY is set and matches the value sent in requests.

# Contact

Project author: Michael Franks <mffranks@pm.me>