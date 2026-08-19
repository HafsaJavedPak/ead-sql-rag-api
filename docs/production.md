# Production Setup and Operations

This repository provides a hardened single-host Compose deployment for the API,
Gradio test console, application PostgreSQL, dummy analytics MySQL, and locally
hosted Langfuse. Compose is suitable for an internal pilot or one-node server.
For high availability, move PostgreSQL, ClickHouse, Redis, MinIO, artifacts, and
Langfuse to redundant managed or Kubernetes-backed services.

## 1. Prepare secrets and model

Install Docker with Compose v2 and start Ollama on the host. Pull the configured
model before starting containers:

```bash
ollama pull gemma4:latest
cp .env.production.example .env.production
openssl rand -base64 64
openssl rand -hex 32
```

Put independent generated values into every password, key, salt, and secret in
`.env.production`. Keep `LANGFUSE_CAPTURE_CONTENT=false` unless prompt and
result content has formal approval for trace storage.

Run the fail-fast configuration check. It prints field names, never secrets:

```bash
.venv/bin/python scripts/check_production_config.py .env.production
```

## 2. Build the dummy analytics database

The source dump contains inserts but no DDL. The generator creates executable
SQLite and MySQL schemas by merging repeated inserts and inferring conservative
column types:

```bash
.venv/bin/python scripts/build_dummy_sqlite.py
```

On the first MySQL container initialization, Compose loads
`ead_dummy_schema.mysql.sql`, then `ead_dummy_data_atomcamp.sql`, then restricts
the `ead_ro` account to `SELECT`. Docker's initialization scripts only run for
an empty `mysql_data` volume.

## 3. Start and verify

```bash
docker compose --env-file .env.production config --quiet
docker compose --env-file .env.production up -d --build
docker compose --env-file .env.production ps
curl --fail http://127.0.0.1:8000/health/live
curl --fail http://127.0.0.1:8000/health/ready
```

Open the Gradio console at `http://127.0.0.1:7860`. Register a user, create a
conversation, send a streaming question, inspect the validated SQL and rows,
and verify any chart in the Chart tab. Open Langfuse at
`http://127.0.0.1:3000` and confirm the same conversation appears as the trace
session. API docs are intentionally disabled in production.

The UI and API ports are loopback-bound. Publish them only through a TLS reverse
proxy with authentication, request-size limits, and rate limits. Do not expose
database, Redis, ClickHouse, or MinIO ports publicly.

## 4. Release checks

```bash
.venv/bin/pytest -q
.venv/bin/ruff check ead_api ead_ui tests scripts/build_dummy_sqlite.py \
  scripts/check_production_config.py
.venv/bin/mypy --follow-imports=skip --ignore-missing-imports \
  ead_api ead_ui scripts/build_dummy_sqlite.py scripts/check_production_config.py
```

Back up application PostgreSQL and every Langfuse state store. The local
artifact volume is not suitable for multiple API replicas; use authenticated
object storage before scaling horizontally. Pin and scan image digests in the
deployment environment before promotion.
