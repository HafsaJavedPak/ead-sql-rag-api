# FastAPI Architecture

Verified against source: middleware ordering against Starlette's
`build_middleware_stack`, event names from a live stream capture, run statuses
and columns from `ead_api/models.py`, database topology from `compose.yaml`.

## 1. Request lifecycle

`add_middleware` inserts at index 0 and the stack is built in reverse, so the
**last registration runs first**. `main.py` registers RequestId, TrustedHost,
then CORS — a request meets CORS first and RequestId last.

```mermaid
flowchart TB
    C["Client (browser)"]
    subgraph MW["Middleware — last registered runs first"]
        direction TB
        SE["ServerErrorMiddleware<br/>framework"]
        CO["CORSMiddleware<br/>registered last → runs first"]
        TH["TrustedHostMiddleware"]
        RI["RequestIdMiddleware<br/>registered first → runs last"]
        EX["ExceptionMiddleware<br/>framework · RFC-9457 problem+json"]
    end
    R["Router + handler<br/>ead_api/api/routers/"]
    D["Dependency resolution<br/>ead_api/dependencies.py"]
    S["Service layer<br/>ead_api/services/"]
    P["Persistence<br/>ead_api/db/base.py"]
    DB[("Application database<br/>PostgreSQL · read-write")]

    C -->|1| SE
    SE -->|2| CO
    CO -->|3| TH
    TH -->|4| RI
    RI -->|5| EX
    EX -->|6| R
    R -->|"7 resolve"| D
    D -->|"8 user + session"| R
    R -->|9| S
    S -->|10| P
    P -->|11| DB
    DB -.->|12| P
    P -.->|13| S
    S -.->|14| R
    R -.->|15| EX
    EX -.->|"16 adds X-Request-ID"| RI
    RI -.->|17| TH
    TH -.->|18| CO
    CO -.->|19| SE
    SE -.->|20| C
```

Steps 7 and 8 run before the handler body; a failed dependency returns 401
without the handler ever executing.

## 2. Dependency resolution

Every provider lives in the single file `ead_api/dependencies.py`. Only
`get_current_user` and `get_auth_context` authorize — the other four supply data
or resources.

```mermaid
flowchart TB
    H["Route handler<br/>user: User = Depends(get_current_user)"]
    A1["get_current_user<br/>AUTHORIZES"]
    A2["get_auth_context<br/>AUTHORIZES"]
    O["oauth2_scheme<br/>reads Bearer header"]
    SS["get_session<br/>yields AsyncSession"]
    GD["get_database<br/>app.state.database"]
    ST["get_settings_from_app<br/>app.state.settings"]

    H --> A1 --> A2
    A2 --> O
    A2 --> SS --> GD
    A2 --> ST
    style A1 fill:#f8e7e3,stroke:#ac3e2e
    style A2 fill:#f8e7e3,stroke:#ac3e2e
```

Dependencies are cached per request, so one `AsyncSession` is shared by every
dependent. `get_session` yields, so the session closes after the response is
sent. Because the check lives in a dependency rather than in each handler, all
23 endpoints behave identically — which is why cross-tenant access consistently
returns 404 rather than leaking existence.

## 3. Streaming a chat turn

`POST /api/v1/conversations/{id}/messages/stream`

```mermaid
sequenceDiagram
    participant B as Browser
    participant F as FastAPI (ead_api)
    participant G as Agent graph (in-process)
    participant D as Application DB

    B->>F: POST /messages/stream (Accept: text/event-stream)
    F->>D: ONE transaction — user msg + assistant placeholder + run (queued)
    D-->>F: COMMIT (before any event)
    F-->>B: message.accepted
    F-->>B: run.started
    F->>G: invoke graph (text, context)
    G-->>F: stage callbacks ×7
    F-->>B: agent.stage ×7
    G-->>F: token callbacks ×N
    F-->>B: assistant.delta ×N
    F-->>B: result.ready
    F-->>B: message.completed | run.failed | run.cancelled
```

State is committed **before** streaming begins, so a dropped connection is
recovered by re-reading the run rather than replaying an in-memory buffer.
Exactly one terminal event is sent.

This is a POST SSE stream — browser `EventSource` only issues GET requests and
cannot send a JSON body, so clients must use streaming `fetch`. It also cannot
be exercised from Swagger UI.

## 4. Run status lifecycle

Statuses are database column values. They are **not** the SSE event names.

```mermaid
stateDiagram-v2
    [*] --> queued: run row created
    queued --> running: work starts
    running --> completed
    running --> failed
    running --> cancelled
    completed --> [*]
    failed --> [*]
    cancelled --> [*]
```

| Run statuses — database column | SSE events — wire protocol |
|---|---|
| `queued` (on creation) | `message.accepted` |
| `running` | `run.started` |
| `completed` · `failed` · `cancelled` | `agent.stage` · `assistant.delta` |
| | `result.ready` |
| | `message.completed` · `run.failed` · `run.cancelled` |

There is no `started` status and no `run.queued` event. Never rename one to
match the other.

## 5. Package boundary and the two databases

```mermaid
flowchart LR
    subgraph API["ead_api"]
        RT["Routers"] --> SV["Services"] --> RUN["SqlAgentRunner<br/>ead_api/agent/runner.py"]
        SV --> APPDB[("Application DB<br/>PostgreSQL · read-write")]
    end
    subgraph AGT["ead_agent — same process"]
        PIPE["LangGraph pipeline<br/>classify → select_schema → generate_sql →<br/>validate_sql → execute_sql → visualize → summarize"]
        GUARD["SELECT-only guard (sqlglot)<br/>rejects writes, DDL, stacked statements"]
        ROE["readonly_engine<br/>user ead_ro"]
        ADE["admin_engine<br/>introspection only"]
        PIPE --> GUARD --> ROE
        PIPE --> ADE
    end
    RUN -->|invoke| PIPE
    PIPE -.->|callbacks| RUN
    ROE -->|"SELECT only"| ANDB[("Analytics DB<br/>MySQL 8.0 · ead_db")]
    ADE -->|"introspection, not guarded"| ANDB
    style GUARD fill:#f8e7e3,stroke:#ac3e2e
```

`admin_engine` bypasses the guard — introspection reads schema metadata, not
model-generated statements.

**The boundary is not network isolation.** `ead_agent` runs in-process inside
the API container, which holds credentials for both databases. It is enforced
at two levels: module ownership (only `ead_agent/db.py` builds analytics
engines) and a database grant —
`GRANT SELECT ON ead_db.* TO 'ead_ro'@'%'` — which is the part with real teeth,
since a write fails at the MySQL server even if every guard above it were
bypassed.

## 6. Data model — application database

```mermaid
erDiagram
    users ||--o{ auth_sessions : has
    users ||--o{ conversations : owns
    conversations ||--o{ messages : contains
    conversations ||--o{ agent_runs : has
    agent_runs ||--o{ artifacts : produces

    users {
        uuid id PK
        string email UK
        string email_normalized
        string password_hash
        string display_name
        string role
        bool is_active
    }
    auth_sessions {
        uuid id PK
        uuid user_id FK
        uuid token_family_id
        string refresh_token_hash
        datetime expires_at
        datetime revoked_at
    }
    conversations {
        uuid id PK
        uuid owner_user_id FK
        string title
        string status
        datetime last_message_at
    }
    messages {
        uuid id PK
        uuid conversation_id FK
        int sequence_no
        string role
        string status
        text content
    }
    agent_runs {
        uuid id PK
        uuid owner_user_id FK
        uuid conversation_id FK
        string status
        text validated_sql
        int row_count
        int retry_count
    }
    artifacts {
        uuid id PK
        uuid owner_user_id FK
        uuid run_id FK
        string kind
        string mime_type
        string storage_path
    }
```

`owner_user_id` on `agent_runs` and `artifacts` is what enforces owner-scoping.
`token_family_id` on `auth_sessions` is what lets refresh-token reuse revoke an
entire family rather than a single token.

LangGraph checkpoints also live in this database, in tables created by the
library's Postgres checkpointer rather than by `ead_api/models.py`.

## 7. Endpoint surface

| Router | Ops | Responsibility |
|---|---|---|
| `health` | 2 | Liveness, and readiness including a database ping |
| `auth` | 5 | Register, login, refresh rotation, logout, logout-all |
| `users` | 2 | Read and update the current profile |
| `conversations` | 6 | Create, list, search, read, rename or archive, soft-delete |
| `messages` | 5 | History, JSON chat, SSE chat, read, soft-delete |
| `runs` | 3 | Run status, cancellation, protected artifact download |

All under `/api/v1` except health. Every private lookup is scoped to the
authenticated owner; a cross-user request returns 404, never 403.
