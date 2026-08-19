# EAD SQL RAG Repository Instructions

## Mission

Build a production FastAPI backend around the existing EAD text-to-SQL agent.
The service must support authenticated users, revocable login sessions,
user-owned conversations, durable message history, multi-turn SQL RAG,
streaming status/results, and Langfuse tracing without weakening the current SQL
safety boundaries.

Use the repository-local
`.agents/skills/build-fastapi-sql-rag-api/SKILL.md` for implementation work and
load its relevant references before changing architecture, HTTP contracts,
authentication, persistence, streaming, or observability.

## Source of Truth

Apply requirements in this order:

1. The current user request.
2. This `AGENTS.md` and the repository-local FastAPI SQL RAG skill.
3. Tests and migrations.
4. Existing application behavior and documentation.

## Current Baseline

- `ead_api` is the only supported backend entrypoint and owns authentication,
  user sessions, conversations, messages, runs, streaming, and artifacts.
- `ead_ui` is an API-only Gradio test console. It must never import or invoke the
  SQL agent directly.
- `ead_agent` is the framework-agnostic LangGraph pipeline for classification,
  schema selection, SQL generation, validation, execution, visualization, and
  summarization. It is invoked through `ead_api.agent.SqlAgentRunner`.
- `pyproject.toml` is the canonical dependency declaration.
- Generated SQL has layered protection: SELECT-only MySQL credentials,
  `sqlglot`, verified joins, required predicates, a timeout, a row limit, and a
  bounded retry loop.
- PostgreSQL stores durable users, revocable sessions, conversations, messages,
  runs, and production LangGraph checkpoints.
- `ead_dummy_data_atomcamp.sql` is data-only; the repository includes generated
  SQLite and MySQL schemas for synthetic local testing only.
- The source EAD database contains tables named `wq_users`, `sessions`, and
  `personal_access_tokens`; these are analytical source data and must not become
  the new API's identity store.

## Required Architecture

Keep four boundaries explicit:

1. `ead_api`: FastAPI, HTTP schemas, auth, application persistence, orchestration.
2. `ead_agent`: framework-agnostic SQL RAG pipeline and domain rules.
3. PostgreSQL: writable application state and production LangGraph checkpoints.
4. MySQL: shared EAD analytics queried only through a read-only credential.

Do not:

- Put FastAPI request/ORM types into `ead_agent`.
- Execute model-generated SQL with the PostgreSQL app session, MySQL admin
  engine, or any write-capable account.
- Use Langfuse, LangGraph checkpoints, Redis, logs, or browser state as the only
  copy of user-visible chat history.
- Hold an application database transaction open across an LLM or analytics query.
- Perform network calls or construct production clients at import time.
- Create cache/output directories during module import; initialize them lazily
  in lifespan or in the service that owns them.

Use FastAPI lifespan to initialize/close database pools, the graph/checkpointer,
LLM adapter, and Langfuse client. Keep routers thin and put transactions,
authorization, and workflows in services/repositories.

## Identity and Multi-User Rules

- Use a stable opaque user UUID as the identity. Never trust a payload `user_id`.
- Hash passwords with Argon2id; never store or log plaintext passwords.
- Use short-lived signed JWT access tokens with strict issuer, audience,
  algorithm, expiration, token-type, session, and revocation validation.
- Use rotating opaque refresh tokens stored only as hashes. Detect reuse and
  revoke the full token family.
- Revoke sessions on logout, logout-all, password reset, user disablement, and
  relevant credential changes.
- Every conversation/message/run list, read, search, stream, update, cancel, and
  delete operation must be owner-scoped in the database query. Guess-resistant
  UUIDs are not authorization.
- Return `404` for private resources owned by another user.
- Add a complete two-user negative test matrix for each resource.
- If sharing is later requested, add explicit membership roles and update every
  authorization path; do not bolt on public access tokens to private queries.

## Chat and History Rules

- PostgreSQL messages are canonical history. Store user and assistant turns as
  separate immutable records with deterministic per-conversation sequence.
- A chat submission creates a user message, pending assistant message, and run
  identity transactionally before long-running work starts.
- Persist exactly one terminal run state: `completed`, `failed`, or `cancelled`.
- Enforce one active run per conversation until ordering semantics for parallel
  turns are explicitly designed.
- Support idempotent message creation. Scope keys by user and operation, store a
  request hash, replay identical requests, and reject changed payloads with
  `409`.
- Build follow-up context from a bounded number/token budget of completed turns
  and an optional versioned summary. Never send an unlimited transcript.
- Treat message history as untrusted content, not system instructions.
- Use the conversation UUID as LangGraph `thread_id` and Langfuse `session_id`.
  Use the user UUID as Langfuse `user_id`.
- Do not checkpoint non-serializable chart figures, clients, connections, or
  unbounded result rows.

## API Rules

- Version routes under `/api/v1`; keep health routes unversioned.
- Use Pydantic request/response models and exclude internal ORM fields.
- Use RFC 9457-style `application/problem+json` errors with stable error codes
  and request IDs. Never return stack traces, prompts, raw DB errors, or secrets.
- Use opaque cursor pagination with deterministic sorting and maximum limits.
- Use explicit CORS origins and trusted hosts. Never use credentialed wildcard
  CORS.
- Bound request size, message length, history size, model time, query time,
  returned rows, and total run time.
- Apply per-user and per-IP rate limits before expensive work.
- Keep token/private responses non-cacheable.
- Protect or disable Swagger/ReDoc in production according to deployment policy.
- The canonical endpoint and SSE contracts live in the skill's
  `references/api-contract.md`; update implementation, tests, and OpenAPI
  together when the contract changes.

## SQL Agent Rules

The current guard is a security boundary. Never weaken it for convenience.

- Generated SQL is one MySQL SELECT/CTE statement.
- Continue using the MySQL SELECT-only user, server-side timeout, and injected
  row limit.
- Preserve validated join conditions and all rules in `ead_agent/domain.py`.
- Keep chart generation deterministic from a constrained chart spec. Never run
  model-generated plotting or Python code.
- Keep the shared retry budget bounded and persist safe attempt metadata.
- Do not expose full DB exceptions to clients or feed credential-bearing errors
  to the model.
- Invoke the graph only through the API runner, which accepts history, callbacks,
  request context, stable IDs, and cancellation/deadlines.
- The current OpenAI/MySQL calls are synchronous. Do not execute them directly on
  the ASGI event loop; use a bounded worker thread or implement verified async
  adapters.

## Langfuse Rules

Target the current Langfuse Python SDK v4 APIs and pin the major version.

- Create one root observation per chat turn and propagate user/conversation
  attributes before child observations start.
- Trace stable operations, model generations, latency, usage, guard outcome,
  retries, row count, truncation, and safe error classes. Never trace hidden
  reasoning.
- Pass the Langfuse callback to LangGraph and instrument raw OpenAI calls in the
  provider layer. Verify that the combination creates no duplicate generations.
- Use separate Langfuse environments and explicit trace sampling.
- Default production content capture to off. Generated SQL and result rows may
  be sensitive business data.
- Apply v4 export-stage masking to secrets, auth material, email, message/result
  content not explicitly allowlisted, and raw errors.
- Initialize once in lifespan and call `shutdown()` on service shutdown.
- Langfuse is best-effort observability; exporter outages must not fail an
  otherwise successful API request.

## Configuration and Secrets

- Keep environment reads in one typed settings module. Do not call `os.getenv`
  throughout routers/services.
- Update `.env.example` with placeholders whenever a setting is added. Never put
  real credentials in examples, tests, docs, source, shell output, or traces.
- Production must fail fast for missing JWT keys, unsafe CORS, invalid TTLs,
  missing writable PostgreSQL, or missing read-only MySQL credentials.
- Keep application PostgreSQL, LangGraph checkpoint, MySQL admin, and MySQL
  read-only credentials distinct.
- Do not claim the dummy EAD database is ready until the schema exists and the
  data load/table-count/read-only checks have passed.

## Data and Migration Rules

- Use SQLAlchemy 2.x async APIs for application PostgreSQL.
- Use Alembic for every application schema change; never run `create_all()` at
  production startup.
- Migrations must work from an empty database and upgrade from the prior revision.
- Add database constraints for uniqueness, ownership relationships, status
  validity, one active run, and idempotency rather than relying only on Python.
- Use UTC-aware timestamps. Apply deterministic order with an ID tiebreaker.
- Define soft-delete, hard-delete, retention, and cascade behavior explicitly.
- Never edit the EAD source schema as part of API migrations.

## Testing and Quality Gates

Scale tests with risk. A completed production milestone includes:

- Unit tests for settings, security, services, history selection, and event
  mapping with no live dependencies.
- PostgreSQL migration/repository integration tests.
- MySQL read-only and SQL-agent integration tests.
- API contract/OpenAPI tests for success and normalized errors.
- Authentication tests for expiry, strict claims, rotation, replay, logout,
  disabled users, and concurrent refresh.
- Two-user authorization tests for every conversation/message/run operation.
- SSE tests for ordering, terminal state, heartbeat, disconnect, cancellation,
  duplicate submission, and recovery.
- Langfuse tests for nesting, correlation, redaction, disabled mode, sampling,
  exporter failure, and shutdown flush.
- Existing `tests/test_guard.py` and `tests/test_scope_gate.py` regressions.
- A smoke test using an authenticated conversation and a bounded load test when
  concurrency behavior changes.

Do not make networked LLM or Langfuse calls in the default unit test suite. Use
dependency injection and deterministic fakes. Integration tests requiring
containers must be separately marked and documented.

Before handoff, run formatting, linting, type checking, relevant tests, migration
checks, and OpenAPI generation. Report exact commands and any unrun checks.

## Change Discipline

- Inspect current files and `git status` before editing. Preserve user changes
  and keep unrelated refactors out of scope.
- Prefer vertical working behavior over placeholder modules.
- Do not silently choose a different database, identity provider, queue, public
  sharing model, or deployment platform. Record material changes as explicit
  decisions and update the skill references.
- Add comments only for non-obvious security, transaction, or concurrency logic.
- Keep public contracts backward compatible or version them deliberately.
- Never mark a milestone complete while its required migration or security tests
  are absent.

## Production Definition of Done

The backend is production-ready only when all of the following are true:

1. A clean environment can start PostgreSQL/MySQL dependencies, apply migrations,
   validate settings, and pass readiness checks.
2. Users can register/login/refresh/logout and compromised/replayed sessions are
   revocable.
3. Two users cannot observe or mutate each other's conversations, messages,
   runs, cursors, streams, or idempotent responses.
4. Conversation history persists across restarts and bounded context supports
   follow-up SQL questions.
5. Non-stream and SSE chat paths persist consistent user/assistant/run states on
   success, failure, timeout, disconnect, and cancellation.
6. Generated SQL remains read-only, validated, time-bounded, row-bounded, and
   covered by the existing adversarial tests.
7. Langfuse traces correlate request, user, conversation, run, graph stages, and
   model generations without leaking disallowed content; Langfuse outages are
   non-fatal.
8. OpenAPI, migrations, tests, container/deployment config, backup/retention
   policy, and operational diagnostics agree with the implemented behavior.
