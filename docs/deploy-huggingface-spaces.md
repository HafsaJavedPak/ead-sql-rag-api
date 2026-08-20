# Deploying to Hugging Face Spaces

> **Requires HF PRO.** Only *static* Spaces are free. Running a Docker
> container — which this app needs, since it's a live FastAPI process, not a
> static site — errors with `402 Payment Required` on `hf repos create
> --sdk docker` unless the account has an HF PRO subscription. If you want a
> deploy target with no payment info at all, use
> [`docs/deploy-render.md`](deploy-render.md) instead — it's the same
> external-services architecture (Neon, Aiven, Groq, Langfuse Cloud), only
> the container host differs.

Same shape as [`docs/deploy-render.md`](deploy-render.md): one lean,
API-only Docker container, every stateful dependency external —
PostgreSQL (Neon), analytics MySQL (Aiven), the LLM (Groq), and tracing
(Langfuse Cloud). The only real differences from the Render path are
mechanical: Spaces routes to a **fixed** port instead of injecting `$PORT`,
and deploys via its own git remote instead of watching this GitHub repo.

Companion files: [`Dockerfile.spaces`](../Dockerfile.spaces) (identical to
`Dockerfile.render` except the port is hardcoded to 8000),
[`README.spaces.md`](../README.spaces.md) (the Space's required frontmatter),
[`.env.spaces.example`](../.env.spaces.example).

## 1. Provision the application database — Neon (PostgreSQL)

Identical to [`docs/deploy-render.md` §1](deploy-render.md#1-provision-the-application-database--neon-postgresql).
Same two-shape URL split (`APP_DATABASE_URL` for asyncpg,
`LANGGRAPH_DATABASE_URL` for the langgraph checkpointer/psycopg).

## 2. Provision analytics MySQL — Aiven free tier

Identical to [`docs/deploy-render.md` §2](deploy-render.md#2-provision-analytics-mysql--aiven-free-tier):
create the free 1GB Aiven MySQL service, load
`ead_dummy_schema.mysql.sql`/`ead_dummy_data_atomcamp.sql` into whichever
database name Aiven assigns (commonly `defaultdb`), create the `ead_ro`
`GRANT SELECT`-only account as `avnadmin`, and get the CA certificate's PEM
content for `DB_SSL_CA` — Aiven enforces TLS on every connection, and
`ead_agent/db.py` needs that certificate to connect at all, not just
securely.

## 3. Get a Groq key and a Langfuse Cloud project

Also identical to `docs/deploy-render.md` §3–4. `LLM_PROVIDER=groq` is
already the config default; Langfuse Cloud's free Hobby tier supplies
`LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY` and a region-specific base URL.
`APP_ENV=production` requires `LANGFUSE_ENABLED=true`
(`ead_api/core/config.py`) — there's no supported way to skip this while
running with production hardening.

## 4. Create the Space

```bash
hf auth login
hf repos create YOUR_USERNAME/ead-sql-rag-api --type space --sdk docker --private
```

(Drop `--private` if you want it public. `--sdk docker` is required —
Spaces builds whatever `Dockerfile` your README frontmatter points at.)

## 5. Push the code, with the Space's README swapped in

The Space's `README.md` needs Hugging-Face-specific YAML frontmatter
(`sdk: docker`, `app_port: 8000`, ...) at the top — that's a different
document from this project's own `README.md`. Do the swap in a disposable
worktree so your actual dev branch is untouched:

```bash
git worktree add ../ead-sql-rag-spaces-deploy HEAD
cd ../ead-sql-rag-spaces-deploy
cp README.spaces.md README.md
git add README.md
git commit -m "Space frontmatter for Docker SDK"
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/ead-sql-rag-api
git push space HEAD:main
cd -
git worktree remove ../ead-sql-rag-spaces-deploy
```

Repeat the `commit` + `push space HEAD:main` two lines whenever you want to
redeploy after code changes — the worktree can stay around between deploys
instead of being recreated each time if you prefer.

## 6. Set secrets and variables

Split matches Spaces' own model: secrets are write-only and hidden, plain
variables are visible. Check `hf spaces secrets add --help` and
`hf spaces variables add --help` for the exact current flag syntax (repeated
`--secrets KEY=VALUE` vs. `--secrets-file`) — both accept a file, which is
the easier route given how many values this needs:

```bash
# Secrets: JWT_SECRET_KEY, APP_DATABASE_URL, LANGGRAPH_DATABASE_URL,
# DB_PASSWORD, DB_READONLY_PASSWORD, DB_SSL_CA, GROQ_API_KEY,
# LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY
hf spaces secrets add YOUR_USERNAME/ead-sql-rag-api --secrets-file secrets.env

# Plain variables: everything else in .env.spaces.example
hf spaces variables add YOUR_USERNAME/ead-sql-rag-api --env-file variables.env
```

`DB_SSL_CA`'s value is the full multi-line PEM certificate content, not a
path — paste it as-is into the secrets file/dashboard field; Spaces stores
it verbatim and `ead_agent/db.py` writes it to a local file at container
startup. Do **not** set `ANALYTICS_DATABASE_URL` — see the comment in
`.env.spaces.example` for why that collapses the two-account separation.

The dashboard's Settings tab does the same thing if you'd rather not use the
CLI for secrets.

## 7. Verify

```bash
hf spaces wait YOUR_USERNAME/ead-sql-rag-api
hf spaces logs YOUR_USERNAME/ead-sql-rag-api --follow
```

```bash
curl --fail https://YOUR_USERNAME-ead-sql-rag-api.hf.space/health/live
curl --fail https://YOUR_USERNAME-ead-sql-rag-api.hf.space/health/ready
```

`/health/ready` pings the application database — a failure there almost
always means the `APP_DATABASE_URL` SSL parameter is wrong (§1). A MySQL
connection failure at startup almost always means `DB_SSL_CA` is missing or
truncated (§2) — Aiven's server will refuse a non-TLS connection outright.

If `TrustedHostMiddleware` rejects requests with a 400, check the logs for
the actual `Host` header the Space's proxy sends and set `ALLOWED_HOSTS` to
match — Spaces' exact hostname routing isn't something to assume in advance.

## 8. Free-tier limitations to expect

- **Cold starts.** Free Spaces sleep after inactivity; the sleep timeout is
  configurable, not fixed — check and set it with
  `hf spaces settings YOUR_USERNAME/ead-sql-rag-api --sleep-time <seconds>`.
- **No persistent disk.** `/app/artifacts` (chart PNGs) resets on every
  restart/redeploy/sleep-wake — same tradeoff as the Render path.
- **Single instance only**, same reasoning as `docs/deploy-render.md` §7 —
  the active-run-per-conversation guarantee and local artifact storage both
  assume one instance.
- **Aiven's free plan is capped at 76 connections and 1GB RAM/disk.** Fine
  for the dummy dataset and a single API instance; don't scale MySQL-side
  concurrency assumptions past that without upgrading the plan.
