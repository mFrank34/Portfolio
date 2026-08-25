# Portfolio

A small personal portfolio backend and static site built with FastAPI and SQLAlchemy (async). This project serves a static frontend (in src/static) and exposes a JSON API for managing projects, skills and blog posts. It uses an async SQLAlchemy engine with a configurable database URL and a simple write-key based protection for mutating operations.

Key features

- FastAPI application serving static pages and a JSON API
- Async SQLAlchemy models and async session management
- Simple content APIs for Projects, Skills and Blog posts
- Markdown-to-sanitized-HTML rendering for blog content
- Static frontend assets in src/static (index.html, blog.html, project.html)

Tech stack

- Python (see Requirements)
- FastAPI
- SQLAlchemy (async)
- aiosqlite (default SQLite async driver)
- Uvicorn for running the ASGI server

Requirements

- Python 3.14+ (as declared in pyproject.toml)
- Install dependencies from pyproject or requirements.txt

Quickstart (development)

1. Clone the repository

   git clone <repo-url>
   cd write-project-readme

2. Create and activate a virtual environment

   python -m venv .venv
   source .venv/bin/activate

3. Install dependencies

   pip install -r requirements.txt

   If you prefer to install from pyproject.toml (PEP 517/518), use your preferred build tool or a modern installer.

4. Configure environment variables

   The project reads configuration from environment variables (and supports a .env file in src/portfolio). The following are relevant:

   - DATABASE_URL — required. Example for local SQLite (provided in src/portfolio/.env):
     sqlite+aiosqlite:///./portfolio.db

   - WRITE_KEY — required. A shared secret used to authorize create/delete operations. Defaults to "changeMe" in the included example .env (change for production).

   - SQL_ECHO — optional. Set to true to enable SQLAlchemy SQL logging.

   You can place these in a .env file at src/portfolio/.env or set them in your shell before running the app. Example .env (already present in the repo):

   DATABASE_URL=sqlite+aiosqlite:///./portfolio.db
   WRITE_KEY=changeMe

5. Run database migrations/creation

   On startup the app will create tables automatically using SQLAlchemy metadata, so there is no separate migration step in this repository. Start the server to initialize the database.

6. Run the app (development)

   From the project root run:

   uvicorn portfolio.main:app --reload --host 0.0.0.0 --port 8000

   - Open http://127.0.0.1:8000/ to view the static site (src/static/index.html)
   - The OpenAPI docs are available at http://127.0.0.1:8000/docs

API overview

Base URL: /api

Projects

- GET /api/project
  - Returns a list of projects (JSON).

- GET /api/project/{slug}
  - Returns a single project by slug.

- POST /api/project
  - Create a project. Request body (JSON):
    { "writeKey": "<WRITE_KEY>", "title": "...", "description": "...", "tech_stack": "...", "url": "..." }

- DELETE /api/project/{project_id}?writeKey=<WRITE_KEY>
  - Delete a project by id. The write key is required as a query parameter.

Skills

- GET /api/skills
  - Returns a list of skills.

- POST /api/skills
  - Create a skill. Request body (JSON):
    { "writeKey": "<WRITE_KEY>", "name": "...", "category": "...", "level": "..." }

- DELETE /api/skills/{skill_id}?writeKey=<WRITE_KEY>
  - Delete a skill by id. The write key is required as a query parameter.

Blog

- GET /api/blog?limit=20&offset=0
  - Returns recent posts with sanitized HTML.

- GET /api/blog/{slug}
  - Returns a single post rendered to HTML.

- POST /api/blog
  - Create a blog post. Request body (JSON):
    { "writeKey": "<WRITE_KEY>", "title": "...", "content_md": "# Markdown content" }

- DELETE /api/blog/{post_id}
  - Delete a post by id. Requires the write key supplied in the X-Write-Key request header.

Security note

This project uses a simple shared WRITE_KEY to protect write/delete endpoints. For production use consider migrating to a stronger auth method (OAuth, API tokens, or JWTs) and protecting the write key using vaults or environment management.

Static frontend

- The static frontend files are in [src/static](/home/frank/Documents/Portfolio.worktrees/write-project-readme/src/static). The FastAPI app mounts this folder at the root so visiting / serves index.html.

Development notes

- The app uses SQLAlchemy async engine with async_sessionmaker and expects the DATABASE_URL to use an async-capable driver (e.g., aiosqlite for SQLite). The included .env defaults to SQLite.
- On startup the application will call Base.metadata.create_all to create tables automatically.
- Tests are not included in this repository. If you add tests, follow the existing project conventions and include a simple test runner command in the README.

Contributing

Contributions are welcome. Please open issues or pull requests with clear descriptions of changes. For code changes, prefer small, focused PRs.

Troubleshooting

- If you see RuntimeError: DATABASE_URL environment variable is not set — set DATABASE_URL either in the environment or in src/portfolio/.env and restart the server.
- If write operations are rejected with 403, ensure WRITE_KEY is set and matches the value sent in requests.

Contact

Project author: Michael Franks <mffranks@pm.me>