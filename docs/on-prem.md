# On-Prem Deployment

## Topology

- FastAPI: public application API on port 8000.
- Application PostgreSQL: users, sessions, chats, runs, and LangGraph state.
- MySQL: EAD analytics database, queried only through an `ead_ro` account.
- Langfuse v3: web, worker, PostgreSQL, ClickHouse, Redis, and MinIO.
- Model server: Groq for hosted development, or local vLLM/Ollama/TGI for
  strict on-prem operation.

Do not expose PostgreSQL, MySQL, ClickHouse, Redis, or MinIO publicly. The
Compose file binds administrative database ports to loopback for development;
remove those host bindings in a shared server deployment.

## Configure

```bash
cp .env.example .env
openssl rand -base64 64   # JWT_SECRET_KEY and NEXTAUTH secret
openssl rand -hex 32      # LANGFUSE_ENCRYPTION_KEY
```

Replace every `change-me`/`replace-me` value. In production set
`APP_ENV=production`, explicit allowed hosts/CORS origins, and retain
`AUTO_CREATE_SCHEMA=false`; Alembic owns schema changes.

For Groq:

```env
LLM_PROVIDER=groq
LLM_MODEL=openai/gpt-oss-120b
GROQ_API_KEY=gsk_...
```

For strict on-prem inference:

```env
LLM_PROVIDER=openai-compatible
LLM_MODEL=<model-served-by-your-runtime>
LOCAL_BASE_URL=http://model-server:8001/v1
LOCAL_API_KEY=not-needed
```

## Load MySQL

For the synthetic environment, generate the inferred MySQL schema and local
SQLite database with `python scripts/build_dummy_sqlite.py`. Compose loads that
schema before `ead_dummy_data_atomcamp.sql` on an empty MySQL volume. For real
EAD data, replace both dummy initialization mounts with a complete reviewed
schema and dump before starting the API.

Create the execution identity after the schema exists:

```sql
CREATE USER IF NOT EXISTS 'ead_ro'@'%' IDENTIFIED BY '<strong-password>';
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'ead_ro'@'%';
GRANT SELECT ON ead_db.* TO 'ead_ro'@'%';
FLUSH PRIVILEGES;
```

Set `DB_READONLY_USER` and `DB_READONLY_PASSWORD` to that identity. Never give
the API's generated-SQL connection DDL or DML privileges.

## Start and migrate

```bash
docker compose config
docker compose up -d --build
docker compose ps
curl --fail http://localhost:8000/health/live
curl --fail http://localhost:8000/health/ready
```

The API container runs `alembic upgrade head` before Uvicorn. The Langfuse
bootstrap variables create the initial local organization, project, user, and
SDK keys. Keep `LANGFUSE_CAPTURE_CONTENT=false` unless prompts and result rows
are approved for tracing; secret fields and bearer tokens are additionally
masked in the SDK.

## Local Python development

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e '.[dev,local]'
cp .env.example .env
.venv/bin/alembic upgrade head
.venv/bin/uvicorn ead_api.main:app --reload
.venv/bin/pytest -q
```

## No-Docker Ollama dummy environment

This mode uses SQLite for both local application state and the generated
analytics database. It is intended for functional testing, not production.

```bash
.venv/bin/python scripts/build_dummy_sqlite.py
```

The command parses all explicit INSERT column lists, merges repeated INSERT
blocks, generates `ead_dummy_schema.sqlite.sql`, and loads
`.local/ead_dummy.db`. The current dump produces 145 unique tables and 4,930
rows. Configure the ignored `.env` as follows:

```env
APP_DATABASE_URL=sqlite+aiosqlite:////absolute/path/.local/app.db
AUTO_CREATE_SCHEMA=true
ANALYTICS_DATABASE_URL=sqlite:////absolute/path/.local/ead_dummy.db

LLM_PROVIDER=openai-compatible
LLM_MODEL=gemma4:latest
LOCAL_BASE_URL=http://127.0.0.1:11434/v1
LOCAL_API_KEY=ollama

EMBED_PROVIDER=lexical
EMBED_MODEL=lexical
LANGFUSE_ENABLED=false
```

Then rebuild catalog metadata and run the API:

```bash
.venv/bin/python scripts/catalog_cli.py --rebuild
.venv/bin/uvicorn ead_api.main:app --host 127.0.0.1 --port 8000
```

The SQLite execution connection enables `PRAGMA query_only=ON`. The SQL parser
guard remains active. Langfuse is disabled in this no-Docker profile; enable
it after starting the local Langfuse service stack.

## Production controls

- Terminate TLS at a reverse proxy and forward `X-Request-ID`.
- Back up both application PostgreSQL and all Langfuse state stores.
- Store environment secrets in a secret manager, not Compose source control.
- Rate-limit authentication and chat endpoints at the ingress.
- Keep API replicas stateless by sharing PostgreSQL and artifact object storage.
- Replace the local artifact volume with authenticated object storage before
  horizontal scaling.
- Pin container image digests and run vulnerability scans before promotion.
- Test refresh-token reuse, cross-tenant 404 behavior, and MySQL write denial in
  every release environment.
