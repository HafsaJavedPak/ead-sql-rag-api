# API Contract

Base URL: `/api/v1`. JSON error responses use a stable `code`, HTTP `status`,
human-readable `detail`, request `instance`, and `X-Request-ID` response header.
All resources except registration, login, refresh, and health require
`Authorization: Bearer <access-token>`.

## Authentication

| Method | Path | Purpose |
|---|---|---|
| POST | `/auth/register` | Create a user and return access/refresh tokens |
| POST | `/auth/jwt/login` | Authenticate and create a server-side session |
| POST | `/auth/jwt/refresh` | Rotate a one-time refresh token |
| POST | `/auth/jwt/logout` | Revoke the current session |
| POST | `/auth/jwt/logout-all` | Revoke every session for the current user |
| GET/PATCH | `/users/me` | Read or update the current profile |

Access tokens expire after 15 minutes by default. Refresh tokens are opaque,
stored only as HMAC hashes, rotated on every use, and revoke their token family
when reuse is detected.

## Conversations and history

| Method | Path | Purpose |
|---|---|---|
| GET/POST | `/conversations` | List or create conversations |
| GET | `/conversations/search?q=...` | Search owned conversations |
| GET/PATCH/DELETE | `/conversations/{id}` | Read, rename, archive, or soft-delete |
| GET | `/conversations/{id}/messages` | Ordered persisted history |
| GET/DELETE | `/messages/{id}` | Read or soft-delete one owned message |
| GET | `/runs/{id}` | Read SQL, result preview, status, and artifacts |
| POST | `/runs/{id}/cancel` | Request cancellation of an active run |

Every lookup includes the authenticated owner ID. Cross-user access returns
404 rather than disclosing whether the resource exists.

## Non-streaming chat

```http
POST /api/v1/conversations/{conversation_id}/messages
Authorization: Bearer <token>
Idempotency-Key: client-generated-unique-key
Content-Type: application/json

{"content":"Which donor funded the most projects?"}
```

The response contains the persisted user message and assistant message. The
assistant message embeds its run, SQL, bounded result preview, and protected
artifact URLs. Repeating the same idempotency key and body returns the original
turn; reusing the key with a different body returns 409.

## Streaming chat

```http
POST /api/v1/conversations/{conversation_id}/messages/stream
Accept: text/event-stream
Authorization: Bearer <token>
Content-Type: application/json

{"content":"Show commitments by year"}
```

This is a POST SSE stream and should be consumed with a streaming `fetch`,
HTTP client, or SDK. Browser `EventSource` only supports GET and cannot submit
the JSON body.

Events are ordered as follows:

1. `message.accepted`: durable IDs for the run and two messages.
2. `run.started`: execution began.
3. `agent.stage`: coarse stages such as `generate_sql` or `execute_sql`.
4. `assistant.delta`: true model-generated answer token chunks.
5. `result.ready`: result metadata and protected image URLs.
6. `message.completed`, `run.failed`, or `run.cancelled`: terminal state.

Each SSE event has a monotonically increasing per-connection `id`. Durable
recovery is done by reading the run or message after reconnecting, not by
replaying an in-memory event buffer.

## Images

Charts are deterministic server-rendered PNG files. The chat response contains
`/api/v1/artifacts/{artifact_id}` URLs rather than embedding unbounded binary
data in the event stream. Artifact downloads require the same bearer token and
are owner-scoped.

## Memory and concurrency

Recent persisted message history is trimmed by message count and approximate
token budget, then used to rewrite follow-up questions into standalone SQL-RAG
questions. LangGraph checkpoints use the conversation ID as `thread_id` and
PostgreSQL in production. Only one queued or running turn is allowed per
conversation; concurrent attempts return 409.
