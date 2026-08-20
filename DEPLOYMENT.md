# Deployment Log — Render + External Services

A detailed, chronological record of deploying `ead-sql-rag-api` to production
on free-tier external services. This is a *log of what actually happened*,
including every error hit and how it was fixed — not a fresh how-to. For a
clean step-by-step guide, see [`docs/deploy-render.md`](docs/deploy-render.md)
and [`docs/deploy-huggingface-spaces.md`](docs/deploy-huggingface-spaces.md).

**No real credentials appear in this file.** Every password, connection
string, and key below is a placeholder (`<LIKE_THIS>`) or a redacted example,
even though real values were exchanged while doing this work. Real values
live only in the Render dashboard, the Neon/Aiven/Groq/Langfuse consoles, and
your own local scratch notes (`ca.pem`, `keys`, `my-keys` — all
`.gitignore`d, never committed).

## 1. Final architecture

```
Browser
  ├─→ Render Static Site (ead_web)        -- the console UI
  │     served from ead_web/, config.js generated at build time
  │
  └─→ Render Web Service (ead_api)        -- Dockerfile.render
        ├─→ Neon PostgreSQL               -- users, sessions, conversations,
        │                                    messages, agent_runs, artifacts,
        │                                    LangGraph checkpoints
        ├─→ Aiven MySQL                   -- EAD analytics data (read-only
        │                                    execution via a GRANT SELECT
        │                                    account, admin account for
        │                                    schema introspection only)
        ├─→ Groq                          -- LLM inference
        └─→ Langfuse Cloud                -- tracing (best-effort)
```

Nothing is self-hosted except the API container itself. This mirrors the
architecture already documented in `docs/system-architecture.md`, just with
every stateful dependency swapped for an external managed service instead of
the bundled Compose stack (`compose.yaml`), per the constraint of using
"services, not cloud infrastructure."

## 2. Path not taken: Hugging Face Spaces

Originally planned to offer both Render and HF Spaces as deploy targets.
Spaces was abandoned after `hf repos create --sdk docker` returned
**`402 Payment Required`**: only *static* Spaces are free — a Docker-runtime
Space (required for a live FastAPI process) needs an HF PRO subscription.
`Dockerfile.spaces`, `README.spaces.md`, and
`docs/deploy-huggingface-spaces.md` still exist in the repo as a documented,
working alternative for anyone with (or willing to get) HF PRO, but the
actual deployed system described in this log is Render-only.

An earlier iteration of the Spaces plan bundled MySQL *inside* the container
(`deploy/spaces/start-spaces.sh`, since removed) to avoid needing an external
MySQL host with `CREATE USER` rights. That approach was dropped once Aiven's
free tier confirmed it grants full admin rights on a dedicated service —
simpler to just use Aiven from both deploy paths.

## 3. External services provisioned

### 3.1 Neon — PostgreSQL (application database)

Free tier. Holds `users`, `auth_sessions`, `conversations`, `messages`,
`agent_runs`, `artifacts` (`ead_api/models.py`) and LangGraph's own
checkpoint tables (created by `checkpointer.setup()`,
`ead_api/main.py:45`).

One connection string, two shapes needed — different client libraries, same
database:

```
APP_DATABASE_URL       = postgresql+asyncpg://<user>:<password>@<host>.aws.neon.tech/<db>?ssl=require
LANGGRAPH_DATABASE_URL = postgresql://<user>:<password>@<host>.aws.neon.tech/<db>?sslmode=require
```

`asyncpg` wants `ssl=require`; the LangGraph checkpointer (`psycopg`) wants
`sslmode=require`. Using the wrong one for either is a silent connection
failure with no helpful error.

Alembic migrations run automatically on every container start
(`Dockerfile.render`'s `CMD`: `alembic upgrade head && uvicorn ...`) — no
manual migration step.

### 3.2 Aiven — MySQL (analytics database)

Free tier: 1GB disk, 1 CPU, 1GB RAM, `max_connections` capped at 76,
dedicated (not shared multi-tenant) service. Pre-created database name was
`defaultdb`, not `ead_db`.

Two accounts, both required — this is a real security boundary in the code
(`ead_agent/db.py`), not a formality:

| Account | Used for | Privileges |
|---|---|---|
| `avnadmin` (Aiven default) | Schema introspection only (`ead_agent/db.py:admin_engine`) | Full, as provisioned by Aiven |
| `ead_ro` (created manually) | The *only* account that ever executes model-generated SQL (`ead_agent/db.py:readonly_engine`) | `GRANT SELECT` only |

Setup commands run (values redacted):

```bash
mysql --user avnadmin --password=<AVNADMIN_PASSWORD> \
  --host <host>.l.aivencloud.com --port <port> defaultdb < ead_dummy_schema.mysql.sql
mysql --user avnadmin --password=<AVNADMIN_PASSWORD> \
  --host <host>.l.aivencloud.com --port <port> defaultdb < ead_dummy_data_atomcamp.sql
```

```sql
CREATE USER 'ead_ro'@'%' IDENTIFIED BY '<EAD_RO_PASSWORD>';
GRANT SELECT ON `defaultdb`.* TO 'ead_ro'@'%';
FLUSH PRIVILEGES;
```

Aiven enforces TLS on every connection — required the `DB_SSL_CA` code
change described in §4.1 below; without it the app could not connect at
all, not just insecurely.

### 3.3 Groq — LLM inference

`LLM_PROVIDER=groq` is already the config default (`ead_api/core/config.py`).
Only needed: a free API key → `GROQ_API_KEY`.

### 3.4 Langfuse Cloud — tracing

Free Hobby tier. `APP_ENV=production` **requires** `LANGFUSE_ENABLED=true`
(`ead_api/core/config.py: Settings.validate_production`) — there is no
supported way to run production hardening with tracing disabled, which is
why Langfuse Cloud was used rather than skipped. `LANGFUSE_CAPTURE_CONTENT`
kept at its default `false` — traces correlate user/conversation/run/stage/
latency/retry-count without exporting question/SQL/result content.
`LANGFUSE_BASE_URL` depends on account region (`https://cloud.langfuse.com`
EU vs `https://us.cloud.langfuse.com` US).

## 4. Code changes made during this deployment

Six substantive code changes were needed, on top of the new deploy-specific
files (Dockerfile.render, render.yaml, docs). All are already committed
(`git log fa21ca8..HEAD` on `master`).

### 4.1 `DB_SSL_CA` support — `ead_agent/config.py`, `ead_agent/db.py`

`ead_agent/db.py` had **zero** SSL handling before this — it could not
connect to any TLS-enforcing managed MySQL host at all. Added
`Settings.db_ssl_ca` (PEM certificate *content*, not a path — the one shape
every deploy target can pass through an env var) and a `_ssl_connect_args()`
helper in `db.py` that writes it to a local cache file once and passes that
path to PyMySQL via `connect_args={"ssl": {"ca": ...}}`, applied to both the
admin and read-only engines.

### 4.2 Surrogate primary keys for 20 tables — `scripts/build_dummy_sqlite.py`

Aiven enforces `sql_require_primary_key`. The generator's `_primary_key()`
only assigns a PK when a table's first INSERT column is uniquely-valued —
never true for junction tables (`course_to_applicants` and 16 others) whose
leading FK column repeats by definition, plus 3 Laravel framework tables
(`cache`, `cache_locks`, `password_reset_tokens`). Fixed in
`mysql_schema_sql()`: any table with no detected primary key now gets a
surrogate `` `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY ``. Regenerated
`ead_dummy_schema.mysql.sql` from this fixed generator — verified all 145
tables now have a PK (was 125/145).

### 4.3 `psycopg[binary]` dependency — `pyproject.toml`

`langgraph-checkpoint-postgres` depends on bare `psycopg` (no extras), which
needs either a system `libpq` or a compiled backend — neither present in the
minimal `python:3.12-slim` images. Surfaced at container startup as
`ImportError: no pq wrapper available`. Fixed by declaring
`psycopg[binary]>=3.1,<4` explicitly in core dependencies — bundles its own
compiled backend, no `apt` package needed in any Dockerfile.

### 4.4 `config.js` loading — `ead_web/index.html`

`app.js` already supported `window.EAD_API_BASE` as a configurable override
(defaulting to `http://127.0.0.1:8000` for local dev), but nothing set it
for a deployed static site. Added `<script src="config.js"></script>`
before `app.js` — absent/404s harmlessly in local dev
(`scripts/serve_web.py`, git-ignored), generated by the Render Static
Site's build command for the deployed console (§5.2).

### 4.5 Server-side exception logging — `ead_api/services/chat.py`

`RunResponse.error_detail` (`ead_api/schemas.py:112`) is returned to the
authenticated caller via `GET /runs/{id}` — so it's deliberately sanitized
to just the exception class name (`AGENTS.md`: never expose raw DB errors to
clients). That meant a failed chat turn was **completely undiagnosable**:
the client only saw "The analysis could not be completed," the DB only
stored e.g. `"Agent failed with OperationalError."`, and nothing was ever
logged server-side at all (the custom `ApiError` handler in
`ead_api/errors.py` just returns JSON, never logs). Added
`logger.exception(...)` in the `except Exception` branch of `stream_turn()`
— full traceback now goes to stdout (visible in Render's Logs tab), while
the client/DB-facing `error_detail` is unchanged.

### 4.6 Refresh-token endpoint crash — `ead_api/services/auth.py`

`POST /api/v1/auth/jwt/refresh` was failing on **every single call** in
production (Postgres only — never surfaced against SQLite/local testing).
`AuthSession.user` is mapped `lazy="joined"` (`ead_api/models.py:104`), so
every `AuthSession` query auto-adds a `LEFT OUTER JOIN users`.
`refresh_session()` also locks the row with `.with_for_update()` for
reuse-detection. Postgres rejects that combination outright: *"FOR UPDATE
cannot be applied to the nullable side of an outer join."* The eager-loaded
`user` was never used in that function anyway — it's fetched separately
three lines later via `session.get(User, ...)`. Fixed with
`.options(noload(AuthSession.user))` on that one query. Diagnosed from the
first real traceback the §4.5 logging produced — see step 15 in §6.

## 5. Render service configuration

### 5.1 API — Web Service

- **Source:** `Dockerfile.render` (lean: no `[local]`/`[ui]` extras, no
  Gradio — base dependencies only, requires `EMBED_PROVIDER=lexical`)
- **Blueprint:** `render.yaml`, deployed via Render dashboard → New →
  Blueprint → this GitHub repo
- **Plan:** free
- **Health check path:** `/health/live`
- **Start command** (baked into the Dockerfile): `alembic upgrade head &&
  uvicorn ead_api.main:app --host 0.0.0.0 --port $PORT` — Render injects
  `$PORT` dynamically for Docker services
- **Live URL:** `https://ead-sql-rag-api.onrender.com`

Full environment variable set (see `.env.render.example` for the annotated
version):

| Variable | Value / source | Notes |
|---|---|---|
| `APP_ENV` | `production` | Fixed in render.yaml |
| `DOCS_ENABLED` | `false` | Fixed |
| `AUTO_CREATE_SCHEMA` | `false` | Fixed — Alembic only |
| `LOG_LEVEL` | `INFO` | Fixed |
| `ALLOWED_HOSTS` | `ead-sql-rag-api.onrender.com` | **No scheme.** Matches the HTTP `Host` header |
| `CORS_ORIGINS` | `https://<static-site>.onrender.com` | **With scheme.** Matches the browser `Origin` header |
| `JWT_SECRET_KEY` | `<generated, 88 chars>` | `openssl rand -base64 64 \| tr -d '\n'` — must be one line, no embedded newline |
| `APP_DATABASE_URL` | Neon, asyncpg shape | §3.1 |
| `LANGGRAPH_DATABASE_URL` | Neon, psycopg shape | §3.1 |
| `DB_HOST` / `DB_PORT` / `DB_NAME` | Aiven | `defaultdb`, not `ead_db` |
| `DB_USER` | `avnadmin` | Admin/introspection only |
| `DB_PASSWORD` | `<avnadmin password>` | |
| `DB_READONLY_USER` | `ead_ro` | |
| `DB_READONLY_PASSWORD` | `<ead_ro password>` | |
| `DB_SSL_CA` | `<full PEM content of Aiven's CA cert>` | Pasted as-is, not a file path — see §4.1 |
| `LLM_PROVIDER` | `groq` | Fixed (also the code default) |
| `GROQ_API_KEY` | `<groq key>` | |
| `EMBED_PROVIDER` | `lexical` | Fixed — required by the lean image |
| `LANGFUSE_ENABLED` | `true` | Fixed — required by `APP_ENV=production` |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` | `<langfuse keys>` | |
| `LANGFUSE_BASE_URL` | `https://cloud.langfuse.com` | Region-dependent |
| `LANGFUSE_CAPTURE_CONTENT` | `false` | Fixed |
| `LANGFUSE_TRACING_ENVIRONMENT` | `production` | Fixed |

### 5.2 Console — Static Site

- **Source:** `ead_web/` (plain HTML/CSS/JS, no build tooling)
- **Root Directory:** blank (deploy from repo root, avoids ambiguity about
  which fields become relative to a subdirectory)
- **Build Command:**
  ```bash
  echo "window.EAD_API_BASE = \"$EAD_API_BASE\";" > ead_web/config.js
  ```
- **Publish Directory:** `ead_web`
- **Environment variable:** `EAD_API_BASE` = `https://ead-sql-rag-api.onrender.com`
- **Plan:** free (Render confirms static sites have no paid requirement,
  unlike Docker/Gradio-runtime Spaces on Hugging Face)

## 6. Troubleshooting log, in order

Every error actually hit during this deployment, and its resolution.

1. **`hf repos create --sdk docker` → `402 Payment Required`.** Docker-SDK
   Spaces need HF PRO; static Spaces are the only free tier. Pivoted
   entirely to Render (§2).

2. **`ERROR 3750 (HY000): Unable to create or change a table without a
   primary key`** loading the schema into Aiven. Root cause and fix: §4.2.

3. **`ERROR 1050 (42S01): Table 'wq_approvalforums' already exists`** on
   retry. The first (failed) load attempt had already created every table
   up to the point of failure. Fixed by generating a single
   `DROP TABLE IF EXISTS <all 145 tables>;` statement and running it before
   reloading the corrected schema.

4. **`ERROR 1396 (HY000): Operation CREATE USER failed`** creating `ead_ro`
   a second time — the account already existed from an earlier attempt.
   Switched to `ALTER USER ... IDENTIFIED BY ...` to reset credentials on
   an existing account instead of re-creating it.

5. **Password with an embedded literal space**, from `openssl rand -base64
   64`'s default line-wrap at 64 characters getting flattened into the SQL
   literal. MySQL accepted it (a space is a legal password character), but
   it's fragile across every place the value gets re-pasted (shell, `.env`,
   dashboard). Regenerated with `openssl rand -hex 24` — hex never wraps
   and has no characters needing escaping anywhere downstream. Same fix
   applied when generating `JWT_SECRET_KEY` (`| tr -d '\n'` after
   `openssl rand -base64 64`, since that value has to stay base64 for the
   app's 48+ character minimum, just without the wrap).

6. **`ERROR 3879 (HY000): Access denied for AuthId avnadmin@% to database
   'sys'`** running `REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'ead_ro'@'%'`
   — a scope-less `REVOKE ALL` has to touch every schema the account could
   conceivably hold privileges on, including `sys`, which Aiven restricts
   even for `avnadmin`. The account was freshly created and had never been
   granted anything beyond `CREATE USER`'s default (nothing), so the
   `REVOKE` step was unnecessary defensive cleanup — dropped it and ran
   `GRANT SELECT` alone. Verified with `SHOW GRANTS FOR 'ead_ro'@'%';`.

7. **`socket.gaierror: [Errno -2] Name or service not known`** connecting
   to Neon — `APP_DATABASE_URL`'s host was
   `ep-wild-cell-ax00xqh2.c-4.us-east-2.tech`, missing the `.aws.neon`
   segment (should be `...us-east-2.aws.neon.tech`). Caused by manually
   retyping part of the connection string instead of copying it whole from
   Neon's dashboard.

8. **`ImportError: no pq wrapper available`** — psycopg had no backend.
   Fixed per §4.3.

9. **Every request returning `400 Bad Request`, including Render's own
   health check**, right after first successful boot. `ALLOWED_HOSTS` was
   still set to a placeholder (`localhost`) from before the service had a
   real hostname. Confirmed via Render's own docs that health-check
   requests carry the service's real `*.onrender.com` hostname as the
   `Host` header — updated `ALLOWED_HOSTS` to
   `ead-sql-rag-api.onrender.com` (no scheme) and it cleared immediately.

10. **`curl https://.../` → `404`.** Not a bug — no route is registered for
    bare `/` (`ead_api/main.py` only mounts `health` unversioned plus
    everything else under `/api/v1`). `/health/live` and `/health/ready`
    are the correct endpoints to check; `/docs` also 404s by design
    (`DOCS_ENABLED=false` in production).

11. **UI sign-up: `Failed to fetch` → `net::ERR_CONNECTION_REFUSED` on
    `http://127.0.0.1:8000`.** Two layered causes:
    - First: the Static Site's Build Command field was empty in Render's
      dashboard, so `config.js` was never generated at all (`404` when
      visited directly).
    - After fixing the Build Command: still failing, because the
      `<script src="config.js">` tag itself (§4.4) had been edited locally
      but never pushed to GitHub — confirmed by diffing
      `origin/master:ead_web/index.html` and finding no reference to
      `config.js` at all. Pushing that commit resolved it.

12. **Confusion over which `https://`-shaped variables need a scheme.**
    Clarified and documented directly in `render.yaml`'s comments:
    `ALLOWED_HOSTS` — bare host, no scheme (matches `Host` header).
    `CORS_ORIGINS`/`EAD_API_BASE` — full origin, with scheme (matches
    `Origin` header / used directly as a fetch base URL).

13. **Chat requests failing with the generic `agent_failed` /
    "The analysis could not be completed."** Client message is intentionally
    sanitized (`AGENTS.md`: never leak raw DB errors), and — discovered
    while investigating — nothing was logged server-side either. Queried
    `agent_runs.error_code`/`error_detail` directly via Neon's SQL Editor as
    an interim diagnostic (works without any code change, since that column
    already existed) and found `OperationalError` / `AdminShutdown` —
    Postgres connection-loss exceptions consistent with Neon's free-tier
    compute auto-suspending after idle and killing sessions mid-transition.
    Added real server-side logging (§4.5) to get the full traceback for
    *future* failures rather than just the exception class name.

14. **Slow responses (not errors).** Determined to be expected free-tier
    behavior, not a bug: Neon's compute waking from suspend, plus a
    one-time-per-container-lifetime schema catalog rebuild against Aiven
    (`ead_agent/schema_catalog.py` — no persistent disk on Render's free
    tier, so this isn't cached across restarts), plus up to 5 sequential
    Groq calls per chat turn. Expected to improve within a warm session and
    degrade again after any real idle gap — inherent to stacking multiple
    scale-to-zero free services, not something to fix.

15. **`POST /api/v1/auth/jwt/refresh` crashing on every call.** Traced via
    the logging added in step 13/§4.5 to a Postgres `FeatureNotSupportedError`
    — full root cause and fix in §4.6.

## 7. Known limitations, accepted as free-tier tradeoffs

- **Cold starts.** Render's free web service sleeps after 15 minutes idle;
  Neon's free compute auto-suspends independently on its own schedule. A
  request can pay both costs stacked.
- **No persistent disk.** Chart PNGs (`/app/artifacts`) and the schema
  catalog cache (`.cache/`) both reset on every restart/redeploy. Chart
  loss is a real (if minor) UX gap; catalog-cache loss just means a slower
  first request per container lifetime, not a correctness issue.
- **Aiven free tier caps:** 1GB disk, 1 CPU, 1GB RAM, 76 max connections.
  Fine for the dummy dataset and single-instance traffic; not something to
  scale concurrency assumptions past without upgrading.
- **Single instance only.** The active-run-per-conversation database
  constraint and local artifact storage both assume exactly one running API
  instance.

## 8. Files added or changed in this deployment work

```
 .env.render.example               |  new
 .env.spaces.example               |  new
 .gitignore                        |  modified (secret-scratch-file excludes)
 Dockerfile.render                 |  new
 Dockerfile.spaces                 |  new (unused in the final deploy, §2)
 README.md                         |  modified (doc links)
 README.spaces.md                  |  new (unused in the final deploy, §2)
 docs/deploy-huggingface-spaces.md |  new (unused in the final deploy, §2)
 docs/deploy-render.md             |  new
 ead_agent/config.py               |  modified (§4.1)
 ead_agent/db.py                   |  modified (§4.1)
 ead_api/services/auth.py          |  modified (§4.6)
 ead_api/services/chat.py          |  modified (§4.5)
 ead_dummy_schema.mysql.sql        |  modified (§4.2, regenerated)
 ead_web/index.html                |  modified (§4.4)
 pyproject.toml                    |  modified (§4.3)
 render.yaml                       |  new
 requirements.txt                  |  new (reference only — pyproject.toml
                                       remains the actual dependency source
                                       of truth, per AGENTS.md)
 scripts/build_dummy_sqlite.py     |  modified (§4.2)
```

Commit range: `fa21ca8` (initial commit) through `c803810` on `master`.
