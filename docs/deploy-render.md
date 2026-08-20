# Deploying to Render on free-tier services

This is a "services, not infrastructure" deployment: Render hosts only the API
container. Every stateful dependency — application PostgreSQL, analytics
MySQL, the LLM, and tracing — is an external managed service you provision
separately and hand to the API as environment variables. Nothing here is a
cloud-provider console (no VMs, no VPCs, no manually managed servers).

Companion files: [`render.yaml`](../render.yaml) (the Blueprint),
[`Dockerfile.render`](../Dockerfile.render) (a lean, API-only image),
[`.env.render.example`](../.env.render.example) (every variable, with the
exact URL rewrites you need). Read [`docs/production.md`](production.md)
first if you have not — this document only covers what's *different* for a
services-based deploy instead of the bundled Compose stack.

## 0. Why this differs from `docs/production.md`

- `compose.yaml` runs Postgres, MySQL, and the entire Langfuse stack
  (web/worker/ClickHouse/Redis/MinIO) as containers with volumes. None of
  that exists on Render's free plan — free web services have no persistent
  disks and are meant to be stateless.
- `APP_ENV=production` makes `Settings.validate_production()`
  (`ead_api/core/config.py`) **require** `LANGFUSE_ENABLED=true`, a real
  48+ character `JWT_SECRET_KEY`, explicit `ALLOWED_HOSTS`/`CORS_ORIGINS`,
  and `AUTO_CREATE_SCHEMA=false`. There is no supported way to run with
  `APP_ENV=production` and Langfuse disabled — so this recipe uses Langfuse
  Cloud's free Hobby tier rather than fighting that validator.
- The root `Dockerfile` installs the `[local,ui]` extras (sentence-transformers
  + torch, plus Gradio) for the Compose stack's `EMBED_PROVIDER=huggingface`
  default. That is too heavy for a free 512MB instance. `Dockerfile.render`
  installs only the base dependencies and requires `EMBED_PROVIDER=lexical`,
  which never loads an embedding model at all
  (`ead_agent/retriever.py:top_k_tables` short-circuits to keyword scoring).

## 1. Provision the application database — Neon (PostgreSQL)

Create a free Neon project and copy the connection string it gives you. It
looks like:

```text
postgresql://USER:PASSWORD@ep-xxxx.neon.tech/neondb?sslmode=require
```

You need it in **two different shapes**, because two different client
libraries read it against the same database:

| Variable | Consumer | Shape |
|---|---|---|
| `APP_DATABASE_URL` | SQLAlchemy, `asyncpg` driver | `postgresql+asyncpg://USER:PASSWORD@ep-xxxx.neon.tech/neondb?ssl=require` |
| `LANGGRAPH_DATABASE_URL` | `langgraph-checkpoint-postgres` (psycopg) | `postgresql://USER:PASSWORD@ep-xxxx.neon.tech/neondb?sslmode=require` |

Note the query parameter is `ssl=require` for the first and `sslmode=require`
for the second — asyncpg and psycopg spell it differently, and using the
wrong one is a silent connection failure, not a helpful error.

Alembic runs automatically on every deploy (`Dockerfile.render`'s `CMD` runs
`alembic upgrade head` before `uvicorn` starts), so you do not need to run
migrations by hand. LangGraph creates its own checkpoint tables on first
startup via `checkpointer.setup()` in `ead_api/main.py`.

## 2. Provision analytics MySQL — Aiven free tier

Aiven's free plan gives a dedicated MySQL 8 service (not a shared multi-tenant
instance): 1GB disk, 1 CPU, 1GB RAM, `max_connections` capped at 76. Create
one, and note four things from its console before continuing:

- **Host and port** — shown as something like
  `mysql-xxxx.f.aivencloud.com` with a service-specific port (not the
  standard `3306`).
- **The default admin user is `avnadmin`**, with its generated password.
- **The pre-created database name** — Aiven's free/starter services come
  with exactly one database already made, commonly `defaultdb`, not the
  `ead_db` name Compose uses locally. Use whatever name Aiven actually gives
  you; the app doesn't care what the database is called.
- **The CA certificate** — Aiven enforces TLS on every connection. Download
  the certificate from the service's connection-info page; you'll need its
  full PEM content (not a path) for `DB_SSL_CA`.

Load the dummy schema and data — neither file contains a `CREATE
DATABASE`/`USE` statement, so this works against whatever database name
Aiven assigned:

```bash
mysql -h <host> -P <port> -u avnadmin -p --ssl-ca=<downloaded-ca.pem> <db_name> \
  < ead_dummy_schema.mysql.sql
mysql -h <host> -P <port> -u avnadmin -p --ssl-ca=<downloaded-ca.pem> <db_name> \
  < ead_dummy_data_atomcamp.sql
```

Then create the second, read-only account. Aiven services are dedicated per
account, so `avnadmin` can run this directly — no separate provider
console/API step needed. This mirrors
[`deploy/mysql/30-readonly-user.sh`](../deploy/mysql/30-readonly-user.sh),
which Compose runs automatically:

```sql
CREATE USER 'ead_ro'@'%' IDENTIFIED BY 'a-strong-generated-password';
GRANT SELECT ON `<db_name>`.* TO 'ead_ro'@'%';
FLUSH PRIVILEGES;
```

Set `DB_SSL_CA` to the CA certificate's PEM content. This is a real code
path, not just configuration — `ead_agent/db.py` had no SSL wiring at all
until this deploy target needed it; it now writes `DB_SSL_CA`'s content to a
local file at startup and passes that path to PyMySQL for both the admin and
read-only engines, since TLS is a property of the connection to Aiven, not
of which account is used.

Verify both accounts work before deploying:

```bash
DB_HOST=<host> DB_PORT=<port> DB_NAME=<db_name> \
DB_USER=avnadmin DB_PASSWORD=<avnadmin-password> \
DB_READONLY_USER=ead_ro DB_READONLY_PASSWORD=<ead_ro-password> \
DB_SSL_CA="$(cat <downloaded-ca.pem>)" \
  .venv/bin/python -c "from ead_agent.db import ping; print(ping())"
```

## 3. Get a Groq API key

`LLM_PROVIDER=groq` is already the default (`ead_api/core/config.py`). Create
a free key at Groq's console and set `GROQ_API_KEY`. No other LLM setup is
needed — Ollama/local-model configuration in `docs/on-prem.md` does not apply
here.

## 4. Create a Langfuse Cloud project

Sign up for Langfuse Cloud's free Hobby tier and create a project. Copy the
public and secret keys, and note which region you're on — the base URL
differs:

- EU: `https://cloud.langfuse.com`
- US: `https://us.cloud.langfuse.com`

Set `LANGFUSE_CAPTURE_CONTENT=false` (the repo's default production posture —
generated SQL and result rows can be sensitive). You'll still get full trace
correlation (user/conversation/run/stage/latency/retry-count); you just won't
export question/answer/SQL text into Langfuse.

## 5. Deploy the Blueprint

In the Render dashboard: **New → Blueprint**, point it at this repository.
Render reads [`render.yaml`](../render.yaml), which:

- Builds `Dockerfile.render` (not the root `Dockerfile`).
- Sets `plan: free` and `healthCheckPath: /health/live`.
- Declares every variable from `.env.render.example` — the ones with fixed
  values are set already; the ones marked `sync: false` prompt you for a
  value in the dashboard before the first deploy.

Fill in every prompted value using what you gathered in steps 1–4. For
`JWT_SECRET_KEY`, generate one the same way `docs/production.md` does:

```bash
openssl rand -base64 64
```

For `ALLOWED_HOSTS`, use the `*.onrender.com` hostname Render assigns the
service (visible in the dashboard once created — you may need to save once,
copy the hostname, then edit the variable and redeploy). For `CORS_ORIGINS`,
use whatever origin will call this API (your `ead_web` deployment, or
`http://localhost:3000` while you're just testing with `scripts/serve_web.py`
locally against the deployed API).

## 6. Verify

```bash
curl --fail https://<your-service>.onrender.com/health/live
curl --fail https://<your-service>.onrender.com/health/ready
```

`/health/ready` pings the application database — a failure there almost
always means the `APP_DATABASE_URL` SSL parameter is wrong (step 1). Then
register a user and send one streaming question, either with `ead_web`
pointed at the deployed API, or directly:

```bash
curl -X POST https://<your-service>.onrender.com/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"a-strong-password"}'
```

Confirm the trace appears in your Langfuse Cloud project, matching the
`conversation_id` you used.

## 7. Free-tier limitations to expect

- **Cold starts.** Render's free web services sleep after 15 minutes idle.
  The first request after a nap pays full container startup — including the
  `alembic upgrade head` step re-running (it's a no-op if already applied,
  but it still connects) — before your SSE stream's first byte.
- **Ephemeral disk.** Chart PNGs land in `/app/artifacts` on local container
  disk. They survive while the instance stays warm, and are lost on every
  redeploy or sleep/wake cycle. Fine for a demo; not durable. If that
  matters later, swap `ead_api/services/chat.py`'s `_copy_artifact` to write
  to an S3-compatible bucket instead (Cloudflare R2's free tier is a common
  service-shaped choice) — out of scope for this first deploy.
- **Single instance only.** The active-run-per-conversation guarantee and
  local artifact storage both assume one instance. Do not scale this service
  to multiple free instances without moving artifacts to shared object
  storage first.
