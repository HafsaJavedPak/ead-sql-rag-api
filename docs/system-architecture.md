# Backend System Architecture

This document is the canonical functional map of the EAD SQL RAG backend. It
shows runtime boundaries, data ownership, request processing, agent execution,
streaming behavior, and the on-prem deployment topology.

## 1. System context

```mermaid
flowchart LR
    User["User or API consumer"]
    UI["Gradio API console"]
    Client["External HTTP client"]
    API["FastAPI service"]
    AppDB[("Application PostgreSQL")]
    Analytics[("EAD analytics MySQL")]
    Model["Ollama, vLLM, TGI, or Groq"]
    Artifacts[("Protected chart storage")]
    Langfuse["Self-hosted Langfuse"]

    User --> UI
    User --> Client
    UI -->|"HTTPS + bearer token"| API
    Client -->|"HTTPS + bearer token"| API
    API -->|"Users, sessions, chats, runs"| AppDB
    API -->|"Validated SELECT only"| Analytics
    API -->|"LangChain model calls"| Model
    API -->|"Write and owner-scoped read"| Artifacts
    API -.->|"Redacted traces, best effort"| Langfuse
```

The Gradio console is not a trusted backend. It stores a user's API tokens in
Gradio session state and exercises the same public endpoints as any other
client. All authorization and ownership checks remain in FastAPI.

## 2. FastAPI functional architecture

```mermaid
flowchart TB
    Request["HTTP request"]

    subgraph Edge["HTTP boundary"]
        Host["Trusted-host validation"]
        Cors["Explicit CORS policy"]
        RequestId["Request ID middleware"]
        Errors["RFC 9457 problem responses"]
    end

    subgraph Routers["Versioned routers"]
        Health["Health and readiness"]
        Auth["Register, login, refresh, logout"]
        Users["Current-user profile"]
        Conversations["Conversation CRUD and search"]
        Messages["History, JSON chat, SSE chat"]
        Runs["Run status and cancellation"]
        ArtifactRoute["Protected artifact download"]
    end

    subgraph Services["Application services"]
        Security["Argon2id, JWT validation, refresh rotation"]
        Ownership["Owner-scoped resource access"]
        Chat["Idempotency and chat orchestration"]
        Context["Bounded persisted history"]
        Runner["Async SQL-agent runner"]
        Observability["Langfuse trace context and masking"]
    end

    subgraph Persistence["Persistence adapters"]
        SQLAlchemy["Async SQLAlchemy sessions"]
        Checkpointer["LangGraph PostgreSQL checkpointer"]
        ReadOnly["Read-only analytics engine"]
        Files["Chart artifact files"]
    end

    Request --> Host --> Cors --> RequestId --> Routers
    Routers --> Errors
    Auth --> Security
    Users --> Ownership
    Conversations --> Ownership
    Messages --> Chat
    Runs --> Chat
    ArtifactRoute --> Ownership
    Security --> SQLAlchemy
    Ownership --> SQLAlchemy
    Chat --> SQLAlchemy
    Chat --> Context --> SQLAlchemy
    Chat --> Observability
    Chat --> Runner
    Runner --> Checkpointer
    Runner --> ReadOnly
    Runner --> Files
```

### Functional ownership

| Function | Primary module | Durable state |
|---|---|---|
| Registration and login | `ead_api.services.auth` | Users and auth sessions |
| Access-token authorization | `ead_api.dependencies`, `ead_api.core.security` | Session revocation state |
| Refresh-token rotation/reuse detection | `ead_api.services.auth` | Hashed refresh-token family |
| Conversation CRUD/search | `ead_api.services.conversations` | Conversations |
| Ordered message history | `ead_api.services.messages` | User and assistant messages |
| Chat idempotency and active-run guard | `ead_api.services.chat` | Agent runs and constraints |
| Streaming SSE protocol | `ead_api.api.routers.messages` | Terminal state is persisted first |
| SQL-RAG execution | `ead_api.agent.runner`, `ead_agent` | Run preview and checkpoints |
| Chart delivery | `ead_agent.charts`, artifact router | PNG file plus ownership metadata |
| Tracing | `ead_api.core.observability` | Langfuse, non-canonical telemetry |

## 3. Authentication and session lifecycle

```mermaid
stateDiagram-v2
    [*] --> Registered: register + Argon2id hash
    Registered --> ActiveSession: issue access + refresh tokens
    ActiveSession --> ActiveSession: access token validates JWT and session
    ActiveSession --> RotatedSession: refresh token used once
    RotatedSession --> ActiveSession: old token revoked, new pair issued
    ActiveSession --> Revoked: logout or logout-all
    RotatedSession --> FamilyRevoked: replaced token reused
    ActiveSession --> Expired: refresh lifetime reached
    Revoked --> [*]
    FamilyRevoked --> [*]
    Expired --> [*]
```

- Access tokens are short-lived JWTs with issuer, audience, algorithm, token
  type, user ID, and session ID validation.
- Refresh tokens are opaque. Only hashes are persisted, and successful refresh
  rotates the token.
- Private resource IDs never authorize access by themselves; database queries
  include the authenticated owner ID and return `404` for other users' data.

## 4. Streaming chat request sequence

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Gradio or HTTP client
    participant API as FastAPI messages router
    participant Auth as Authentication dependency
    participant DB as Application PostgreSQL
    participant Trace as Langfuse context
    participant Agent as SQL-agent runner
    participant LLM as LangChain model provider
    participant MySQL as EAD MySQL read-only
    participant Files as Artifact storage

    User->>UI: Submit question
    UI->>API: POST messages/stream + bearer token
    API->>Auth: Validate JWT and live session
    Auth->>DB: Load user and non-revoked session
    API->>DB: Lock owned conversation and check idempotency
    API->>DB: Commit user message, pending assistant, and queued run
    API-->>UI: message.accepted
    API-->>UI: run.started
    API->>DB: Load bounded completed history
    API->>Trace: Start user/session/run-correlated trace
    API->>Agent: Stream graph with history and callbacks
    Agent-->>UI: agent.stage
    Agent->>LLM: Classify, select schema, generate SQL
    Agent->>Agent: Parse and validate one SELECT/CTE
    Agent->>MySQL: Execute with timeout and row limit
    MySQL-->>Agent: Bounded columns and rows
    Agent->>LLM: Stream grounded summary
    Agent-->>UI: assistant.delta events
    opt Chart requested by constrained specification
        Agent->>Files: Render deterministic PNG
    end
    API->>DB: Commit completed message, run, SQL, preview, artifact metadata
    API-->>UI: result.ready
    API-->>UI: message.completed
    UI->>API: GET protected artifact with bearer token
    API->>DB: Verify artifact owner
    API-->>UI: PNG file
```

If the client disconnects, cancellation is requested and the run is persisted as
cancelled when execution observes it. If execution fails, clients receive a
sanitized `run.failed` event while raw stack traces and database credentials stay
server-side.

## 5. SQL-RAG agent state machine

```mermaid
flowchart LR
    Start(["Question + bounded history"])
    Classify["Classify scope and write intent"]
    Refuse["Return safe refusal"]
    Retrieve["Retrieve candidate schema"]
    Refine["LLM table refinement"]
    Connect["Deterministic join-graph connection"]
    Generate["Generate one SQL statement"]
    Guard["sqlglot and domain-rule validation"]
    Execute["Read-only execution with timeout and LIMIT"]
    Viz["Choose constrained chart specification"]
    Render["Render deterministic PNG"]
    Summarize["Stream grounded answer"]
    Retry{"Retry budget available?"}
    Reselect{"Wrong-table or join failure?"}
    Fail["Persist sanitized failure"]
    Done(["Completed run"])

    Start --> Classify
    Classify -->|"Irrelevant or write request"| Refuse --> Done
    Classify -->|"Answerable"| Retrieve --> Refine --> Connect --> Generate --> Guard
    Guard -->|"Valid"| Execute
    Guard -->|"Rejected"| Retry
    Execute -->|"Success"| Viz --> Render --> Summarize --> Done
    Execute -->|"Database error"| Retry
    Retry -->|"No"| Fail
    Retry -->|"Yes"| Reselect
    Reselect -->|"Yes"| Retrieve
    Reselect -->|"No"| Generate
    Fail --> Done
```

The retry paths share one bounded counter. SQL validation remains a security
boundary even when the model, schema retriever, or database returns an error.

## 6. Data ownership and trust zones

```mermaid
flowchart TB
    subgraph Writable["Writable application trust zone"]
        UsersTable[("users")]
        SessionsTable[("auth_sessions")]
        ConversationsTable[("conversations")]
        MessagesTable[("messages")]
        RunsTable[("agent_runs and artifacts")]
        GraphState[("LangGraph checkpoints")]
    end

    subgraph ReadOnlyZone["Read-only analytical trust zone"]
        SourceTables[("EAD domain tables")]
        InfoSchema[("information_schema metadata")]
    end

    subgraph Telemetry["Best-effort telemetry zone"]
        Traces[("Langfuse traces")]
        TraceStores[("Langfuse PostgreSQL, ClickHouse, Redis, MinIO")]
    end

    APIService["FastAPI service"] -->|"Read/write ORM"| UsersTable
    APIService -->|"Session and chat persistence"| ConversationsTable
    APIService -->|"Validated SELECT only"| SourceTables
    APIService -->|"Schema introspection"| InfoSchema
    APIService -.->|"Masked export"| Traces --> TraceStores
```

PostgreSQL messages are canonical chat history. LangGraph checkpoints support
execution continuity, and Langfuse supports diagnostics; neither replaces
user-visible message persistence.

## 7. Single-host Compose topology

```mermaid
flowchart LR
    Browser["Browser"]
    Ollama["Host Ollama API"]

    subgraph DockerHost["Docker host"]
        UIContainer["Gradio :7860"]
        APIContainer["FastAPI :8000"]
        AppPostgres[("App PostgreSQL")]
        MySQL[("Analytics MySQL")]

        subgraph LangfuseStack["Langfuse v3 stack"]
            LFWeb["Web :3000"]
            LFWorker["Worker"]
            LFPostgres[("PostgreSQL")]
            ClickHouse[("ClickHouse")]
            Redis[("Redis")]
            MinIO[("MinIO")]
        end

        ArtifactVolume[("Artifact volume")]
    end

    Browser --> UIContainer --> APIContainer
    Browser --> LFWeb
    APIContainer --> AppPostgres
    APIContainer --> MySQL
    APIContainer --> ArtifactVolume
    APIContainer --> Ollama
    APIContainer -.-> LFWeb
    LFWeb --> LFPostgres
    LFWeb --> ClickHouse
    LFWeb --> Redis
    LFWeb --> MinIO
    LFWorker --> LFPostgres
    LFWorker --> ClickHouse
    LFWorker --> Redis
    LFWorker --> MinIO
```

Only the UI, API, and Langfuse web interfaces should be reachable through a TLS
reverse proxy. Database and telemetry storage ports remain private. The supplied
Compose topology is appropriate for local development and single-host pilots;
high availability requires externalized redundant state services and shared
artifact object storage.

## 8. Endpoint capability map

| Capability | Endpoint |
|---|---|
| Register | `POST /api/v1/auth/register` |
| Login and rotate refresh token | `POST /api/v1/auth/jwt/login`, `/refresh` |
| Revoke one or all sessions | `POST /api/v1/auth/jwt/logout`, `/logout-all` |
| Read/update current profile | `GET/PATCH /api/v1/users/me` |
| Create/list/search conversations | `GET/POST /api/v1/conversations`, `GET /search` |
| Read/update/archive/delete conversation | `GET/PATCH/DELETE /api/v1/conversations/{id}` |
| Read ordered history | `GET /api/v1/conversations/{id}/messages` |
| Non-streaming chat | `POST /api/v1/conversations/{id}/messages` |
| Streaming chat | `POST /api/v1/conversations/{id}/messages/stream` |
| Inspect or cancel run | `GET /api/v1/runs/{id}`, `POST /cancel` |
| Download owner-scoped chart | `GET /api/v1/artifacts/{id}` |
| Liveness/readiness | `GET /health/live`, `GET /health/ready` |
