# EAD SQL RAG API

Authenticated, multi-user FastAPI backend for conversational text-to-SQL over
the Economic Affairs Division dataset. The service provides revocable JWT
sessions, durable chat history, streaming responses, protected chart artifacts,
LangGraph memory, and optional self-hosted Langfuse tracing.

## Supported entrypoints

```bash
# API
.venv/bin/uvicorn ead_api.main:app --host 127.0.0.1 --port 8000

# Web console (default UI)
.venv/bin/python scripts/serve_web.py

# API-backed Gradio test console
.venv/bin/python -m ead_ui.app
```

Both UIs communicate only through the authenticated HTTP API. Neither imports or
invokes the SQL agent directly. `ead_web` is the default console; `ead_ui` is a
Gradio test harness kept for quick API probing.

| Service | Local URL |
|---|---|
| Web console, default UI | `http://localhost:3000` |
| API docs, development only | `http://127.0.0.1:8000/docs` |
| API readiness | `http://127.0.0.1:8000/health/ready` |
| Gradio API console | `http://127.0.0.1:7860` |
| Langfuse, Compose deployment | `http://127.0.0.1:3000` |

Note the port overlap: the web console and Langfuse both default to 3000. They
do not collide in the local no-Docker profile, where `LANGFUSE_ENABLED=false`.
When running the Compose stack, serve the console elsewhere with
`python scripts/serve_web.py --port 3001` and add that origin to `CORS_ORIGINS`.

## Local Ollama workflow

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e '.[dev,ui]'
cp .env.example .env
.venv/bin/python scripts/build_dummy_sqlite.py
.venv/bin/python scripts/catalog_cli.py --rebuild
.venv/bin/uvicorn ead_api.main:app --host 127.0.0.1 --port 8000
```

Configure `.env` with SQLite application and analytics URLs, an
OpenAI-compatible Ollama URL, and `EMBED_PROVIDER=lexical`. The exact local
settings are documented in [on-prem operations](docs/on-prem.md).

## Production Compose workflow

```bash
cp .env.production.example .env.production
# Replace every placeholder with an independent secret.
.venv/bin/python scripts/check_production_config.py .env.production
.venv/bin/python scripts/build_dummy_sqlite.py
docker compose --env-file .env.production config --quiet
docker compose --env-file .env.production up -d --build
```

The Compose stack includes the API, Gradio console, application PostgreSQL,
read-only analytics MySQL, and the Langfuse web/worker data services. It is a
single-host deployment, not a high-availability topology.

## Architecture

- [Backend system diagrams](docs/system-architecture.md)
- [API contract](docs/api.md)
- [Production runbook](docs/production.md)
- [On-prem and local setup](docs/on-prem.md)

## Repository layout

```text
ead_api/        FastAPI, authentication, persistence, chat orchestration, SSE
ead_agent/      Framework-agnostic SQL-RAG graph and SQL safety rules
ead_web/        Default web console, a browser client of the HTTP API
ead_ui/         Gradio client of the authenticated FastAPI endpoints
migrations/     Alembic application-database migrations
deploy/         Container initialization helpers
scripts/        Database bootstrap, schema catalog, production preflight
tests/          API, security, SQL guard, tracing, UI-client tests
docs/           API, architecture, deployment, and operations documentation
```

`pyproject.toml` is the only dependency source of truth.

## Security boundaries

- Generated SQL executes only through the analytics read-only credential.
- `sqlglot` rejects writes, stacked statements, unsafe joins, and prohibited
  constructs before execution.
- PostgreSQL owns users, refresh-token sessions, conversations, messages, and
  runs; analytical source tables never serve as the identity store.
- Every private resource query is scoped to the authenticated owner.
- Charts are rendered from constrained specifications; model-generated Python is
  never executed.
- Langfuse content capture defaults off and export-stage masking removes secrets,
  authentication material, email addresses, and disallowed content.

## Quality gates

```bash
.venv/bin/pytest -q
.venv/bin/ruff check ead_api ead_agent ead_ui tests \
  scripts/build_dummy_sqlite.py scripts/catalog_cli.py \
  scripts/check_production_config.py
.venv/bin/mypy --follow-imports=skip --ignore-missing-imports \
  ead_api ead_ui scripts/build_dummy_sqlite.py \
  scripts/check_production_config.py
```

The synthetic schema generated from sample inserts is for local and test use.
Production EAD deployments require a reviewed authoritative schema and dump.
