# URL Shortener Service

Production-oriented async Python URL shortener using FastAPI, async SQLAlchemy, asyncpg, Redis, Uvicorn, uv, Loguru, and Alembic.

## Features

- Create short URLs using Base62 encoded IDs.
- Optional custom aliases.
- Fast redirect path with Redis cache-first lookup.
- Async analytics event publishing.
- Daily click aggregation.
- PostgreSQL persistence.
- Async SQLAlchemy + asyncpg.
- Redis cache and lightweight Redis Streams analytics queue.
- Alembic migrations.
- Docker Compose for local development.
- Health checks, structured logging, settings, and tests.

## Local setup

```bash
uv sync
cp .env.example .env
docker compose up -d postgres redis
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Create a URL:

```bash
curl -X POST http://localhost:8000/api/v1/urls \
  -H 'Content-Type: application/json' \
  -d '{"long_url":"https://example.com/a/very/long/url"}'
```

Redirect:

```bash
curl -i http://localhost:8000/<alias>
```

Run analytics worker:

```bash
uv run python -m app.workers.analytics_worker
```

Run tests:

```bash
uv run pytest
```

## Architecture

```text
Client
  -> Load Balancer / CDN
  -> FastAPI Redirect Service
  -> Redis cache
  -> PostgreSQL URL mapping database
  -> Redis Stream click_events
  -> Analytics Worker
  -> PostgreSQL aggregated analytics tables
```

The redirect path never blocks on analytics writes. It publishes a small event to Redis Streams and returns the redirect immediately.

For very large production scale, Redis Streams can be replaced with Kafka, Pub/Sub, or SQS without changing the redirect API significantly.
