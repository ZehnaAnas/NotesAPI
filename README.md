# Notes API

A production-patterned REST service for note management, built to demonstrate a decoupled, async-first backend architecture: a stateless API layer, a connection-pooled relational store, a cache-aside read path, and an out-of-band task execution layer for non-request-blocking workloads.

## Architecture Overview

The system follows a **layered service architecture** with clear separation of concerns:

```
Client
  │
  ▼
FastAPI (ASGI, ports 8000) ── ORM layer (SQLAlchemy/SQLModel) ── PostgreSQL (Supabase, managed)
  │
  ├── Cache-aside reads/invalidation ── Redis (in-memory KV store)
  │
  └── Task enqueue (.delay()) ── Redis (message broker) ── Celery worker pool (separate process/container)
```

Each service runs as an isolated container, orchestrated via Docker Compose, communicating over a bridge network by service name rather than hardcoded hosts, this keeps the topology environment-agnostic and horizontally scalable in principle (each service could be replicated independently in a production deployment).

## Tech Stack

| Layer | Tool | Role |
|---|---|---|
| API framework | FastAPI (ASGI) | Async request handling, dependency injection, auto-generated OpenAPI schema |
| ORM | SQLAlchemy / SQLModel | Declarative models, session-scoped unit-of-work pattern |
| Schema migrations | Alembic | Versioned, revertible DDL changes via autogenerate diffing |
| Persistence | PostgreSQL (Supabase, pooled connection) | ACID-compliant relational store |
| Caching | Redis | Cache-aside pattern for read-heavy endpoints, TTL-based expiry |
| Async task queue | Celery + Redis broker | Decoupled background job execution, task state tracking |
| Containerization | Docker / Docker Compose | Multi-service orchestration, reproducible builds |

## Design Patterns & Concepts Implemented

- **Dependency Injection**: database sessions are yielded per-request via FastAPI's `Depends()`, ensuring proper session lifecycle management and avoiding connection leaks.
- **Cache-Aside (Lazy Loading)**: reads check Redis first; on a miss, the DB is queried and the result is written back to cache with a TTL. Writes explicitly invalidate the relevant cache keys rather than relying on expiry alone, minimizing staleness windows.
- **Producer-Consumer via Message Broker**: the API acts as a producer, pushing task messages onto a Redis-backed queue; Celery workers act as consumers, polling and executing independently of the request lifecycle. This decouples task execution time from HTTP response time entirely.
- **Idempotent Task Design**: background tasks are structured to tolerate at-least-once delivery semantics (a property of most message brokers) without producing duplicate side effects on retry.
- **Process Isolation**: Celery workers run in a separate process/container from the API and instantiate their own DB sessions — no shared memory or connection state with the request-handling process.
- **Schema Versioning**: Alembic migrations are treated as an append-only, reviewable history of DDL changes rather than ad-hoc manual schema edits, enabling rollback and reproducibility across environments.

## Project Structure

```
NotesAPI/
├── main.py              # FastAPI app, route definitions, startup lifecycle hooks
├── database.py           # Engine/session factory, ORM model definitions
├── celery_app.py          # Celery application instance and broker/backend config
├── tasks.py               # Task definitions (digest generation, etc.)
├── Redis/
│   └── cache.py           # Redis client, cache-aside helper functions
├── alembic/
│   ├── env.py              # Migration environment config
│   └── versions/            # Ordered migration revision history
├── alembic.ini
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env                      # Runtime configuration (excluded from VCS)
```

## Getting Started

### Prerequisites
- Docker & Docker Compose
- A PostgreSQL-compatible connection string (Supabase pooler endpoint recommended over direct connection for containerized workloads)

### 1. Clone
```bash
git clone https://github.com/<your-username>/notes-api.git
cd notes-api
```

### 2. Configure environment
```env
PASSWORD=your_supabase_db_password
```
> Swap for a full `DATABASE_URL` env var if you refactor `database.py` toward a single-source-of-truth connection string.

### 3. Bring up the stack
```bash
docker compose up --build
```
Spins up three services on a shared Docker network:
- `web` — FastAPI application server (Uvicorn, ASGI, bound to `0.0.0.0:8000` for container-external reachability)
- `redis` — dual-purpose: Celery message broker + application cache
- `worker` — Celery worker process consuming from the Redis queue

### 4. Apply migrations
```bash
docker compose exec web alembic upgrade head
```

### 5. Interact
```
http://localhost:8000/docs
```
Auto-generated OpenAPI/Swagger interface for schema inspection and manual endpoint testing.

## API Surface

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/notes` | Create a note (write-path, triggers cache invalidation) |
| `GET` | `/notes` | List notes (read-path, cache-aside) |
| `GET` | `/notes/{note_id}` | Fetch a single note by primary key |
| `PUT` | `/notes/{note_id}` | Update a note (write-path, triggers cache invalidation) |
| `DELETE` | `/notes/{note_id}` | Delete a note (write-path, triggers cache invalidation) |
| `POST` | `/notes/digest` | Enqueue an async digest job; returns a `task_id` immediately (non-blocking) |
| `GET` | `/notes/digest/{task_id}` | Poll task state (`PENDING`/`SUCCESS`/`FAILURE`) and retrieve result once resolved |

## Roadmap / Possible Extensions
- Auth layer (JWT-based, scoped per-user notes)
- Rate limiting on write endpoints
- Structured logging + request tracing across the API/worker boundary
- Read replicas or connection pooler tuning for higher concurrency

## License
MIT
