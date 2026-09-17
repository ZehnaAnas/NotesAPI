# Notes API

A REST API for managing notes, built as a hands-on project to learn backend fundamentals: FastAPI, SQLAlchemy/SQLModel, Alembic migrations, PostgreSQL (via Supabase), Redis caching, background task processing with Celery, and Docker.

## Features

- Full CRUD for notes (create, read, update, delete)
- Search/filter notes by tag
- Redis caching on read-heavy endpoints, with cache invalidation on writes
- Background "weekly digest" job that summarizes notes asynchronously via Celery, with a status-check endpoint
- Database schema managed through Alembic migrations
- Fully containerized with Docker Compose — app, Redis, and Celery worker run together with one command

## Tech Stack

| Layer | Tool |
|---|---|
| API framework | FastAPI |
| ORM | SQLAlchemy / SQLModel |
| Migrations | Alembic |
| Database | PostgreSQL (hosted on Supabase) |
| Caching | Redis |
| Background jobs | Celery |
| Containerization | Docker & Docker Compose |

## Project Structure

```
NotesAPI/
├── main.py              # FastAPI app and route definitions
├── database.py           # SQLAlchemy/SQLModel engine, session, and models
├── celery_app.py          # Celery app configuration
├── tasks.py               # Celery background tasks (e.g. digest generation)
├── Redis/
│   └── cache.py           # Redis connection and caching helpers
├── alembic/
│   ├── env.py
│   └── versions/           # Migration history
├── alembic.ini
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env                     # Environment variables (not committed)
```

## Getting Started

### Prerequisites
- Docker and Docker Compose installed
- A Supabase project (or any PostgreSQL database) with a connection string

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/notes-api.git
cd notes-api
```

### 2. Set up environment variables
Create a `.env` file in the project root:
```env
PASSWORD=your_supabase_db_password
```
> Adjust this to match whatever variables `database.py` expects (e.g. a full `DATABASE_URL` if you refactor to that pattern).

### 3. Run with Docker Compose
```bash
docker compose up --build
```
This starts three services:
- `web` — the FastAPI app (port `8000`)
- `redis` — the Redis cache and Celery message broker
- `worker` — the Celery worker that processes background tasks

### 4. Apply database migrations
```bash
docker compose exec web alembic upgrade head
```

### 5. Explore the API
Once running, open:
```
http://localhost:8000/docs
```
This is FastAPI's interactive Swagger UI — every endpoint can be tested directly from the browser.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/notes` | Create a new note |
| `GET` | `/notes` | List all notes (cached) |
| `GET` | `/notes/{note_id}` | Get a single note by ID |
| `PUT` | `/notes/{note_id}` | Update a note |
| `DELETE` | `/notes/{note_id}` | Delete a note |
| `POST` | `/notes/digest` | Trigger a background digest job, returns a `task_id` |
| `GET` | `/notes/digest/{task_id}` | Check the status/result of a digest job |

## What This Project Demonstrates

- Wiring FastAPI to a cloud-hosted Postgres database through SQLAlchemy
- Managing schema changes safely with Alembic instead of manual table edits
- Implementing the cache-aside pattern with Redis, including invalidation on writes
- Offloading slow work to a background worker with Celery, and polling for results instead of blocking requests
- Running a multi-service application (API + cache + worker) with Docker Compose

## Notes / Gotchas Learned Along the Way

- Uvicorn must bind to `0.0.0.0` inside a container, not `localhost` — otherwise the app is unreachable from outside the container even with ports mapped correctly.
- Inside Docker's network, services reach each other by service name (e.g. `redis`), not `localhost`.
- Celery workers don't hot-reload — restart the worker container after changing task code.
- Task functions run in a separate process from the API, so they need their own database session rather than reusing one from the request.

## License
MIT
