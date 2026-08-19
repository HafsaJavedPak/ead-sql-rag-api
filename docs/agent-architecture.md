# SQL-RAG Agent Architecture

The `ead_agent` package: a LangGraph text-to-SQL pipeline over the EAD analytics
database. It knows nothing about users, HTTP, or authentication — it takes a
question and returns an answer, the SQL that produced it, and optionally a chart.

Verified against source: graph topology from `ead_agent/graph.py`, stage mapping
from `ead_api/agent/runner.py`, guard checks from `ead_agent/nodes/validate_sql.py`,
defaults from `ead_agent/config.py`.

## 1. The graph

Thirteen nodes and three conditional branches. The scope gate runs **first**, so
an irrelevant or write-intent question ends at `refuse` having generated no SQL
and touched no table.

```mermaid
flowchart TD
    START([entry]) --> CL["classify<br/>scope gate"]
    CL -->|"irrelevant / write_request"| RF["refuse"]
    RF --> E1([END])

    CL -->|answerable| SS["select_schema"]
    SS --> GS["generate_sql"]
    GS --> VS["validate_sql<br/>SELECT-only guard"]

    VS -->|ok| EX["execute_sql<br/>readonly_engine"]
    VS -->|"hallucinated join<br/>needs_reselect"| BR2["bump_and_reselect"]
    VS -->|"rejected"| BR1["bump_retry"]
    VS -->|"budget spent"| FA["fail"]

    EX -->|ok| DV["decide_visualization"]
    EX -->|"database error"| BR1
    EX -->|"budget spent"| FA

    BR2 --> SS
    BR1 --> GS

    DV --> RC["render_chart"]
    RC -->|"include_summary=True"| SU["summarize"]
    RC -->|"include_summary=False<br/>API streams it instead"| E2([END])
    SU --> E3([END])
    FA --> E4([END])

    style VS fill:#f8e7e3,stroke:#ac3e2e
    style RF fill:#f8e7e3,stroke:#ac3e2e
    style FA fill:#f8e7e3,stroke:#ac3e2e
    style BR1 fill:#f7eedf,stroke:#8f5e10
    style BR2 fill:#f7eedf,stroke:#8f5e10
```

**One retry budget, two repair paths.** Guard rejections and database errors feed
the same counter, so a query rejected twice then erroring once still stops at
`MAX_RETRIES` (default 3) total.

The two paths differ in where they re-enter:

| Path | Re-enters at | Used when |
|---|---|---|
| `bump_retry` | `generate_sql` | The SQL was wrong — regenerate with the error as a hint |
| `bump_and_reselect` | `select_schema` | The **tables** were wrong. Regenerating against the same table set reproduces the same bad join, so the offending table is excluded and selection runs again |

`execute_sql` captures database errors into state rather than raising, so the
graph can route back with the database's own message as grounded feedback.

## 2. Nodes are not stages

The API collapses 13 graph nodes into 7 `agent.stage` event names, and suppresses
consecutive duplicates. This is why a stream shows seven stages regardless of how
many nodes actually ran.

Five nodes map one-to-one onto the stage of the same name. Only these six are
interesting:

```mermaid
flowchart LR
    n6["decide_visualization"] --> s6["visualize"]
    n7["render_chart"] --> s6
    n8["refuse"] --> s7["summarize"]
    n9["fail"] --> s7
    n10["bump_retry"] -.-> X["no event emitted"]
    n11["bump_and_reselect"] -.-> X
    style s6 fill:#e2eee9,stroke:#1f6f5c
    style s7 fill:#e2eee9,stroke:#1f6f5c
    style X fill:#f7eedf,stroke:#8f5e10
```

Two collapses and two silences. `decide_visualization` and `render_chart` both
report `visualize`; `refuse` and `fail` both report `summarize` — so a refusal
looks like a normal turn ending, from the client's point of view.

The retry nodes emit nothing at all, which means **a repair loop is invisible in
the event stream**. The runner also suppresses consecutive duplicates, so a
rejected statement that regenerates and passes shows `generate_sql` once, not
twice. Use `retry_count` on the run record to see repairs, not the event log.

## 3. Schema selection — three phases

146 tables times ~9 columns will not fit in a prompt, and stuffing them in would
bury the signal even if it did.

```mermaid
flowchart LR
    Q["question"] --> R["1 · retrieve<br/>embeddings + lexical<br/>top-K, K=25"]
    R --> RF["2 · refine<br/>one cheap LLM call<br/>picks the final 3-8"]
    RF --> C["3 · connect<br/>deterministic join-graph walk<br/>adds junction tables"]
    C --> OUT["schema_text + join_text<br/>handed to generate_sql"]
    CAT[("schema catalog<br/>.cache/schema_catalog.json")] -.-> R
    CAT -.-> C
    style C fill:#e2eee9,stroke:#1f6f5c
```

**Phase 3 is deliberately not delegated to the model.** With one real foreign key
in the whole schema, a hallucinated join condition is the most likely way to get
a wrong answer that still executes. The join graph is inferred once and walked
deterministically.

Selection also steers away from look-alike tables. `project_to_foreigndetails`
is a per-tranche sub-breakdown with far fewer rows than
`project_to_foreigncecomponents`; picking it silently undercounts. The canonical
table wins unless the question contains an explicit trigger word such as
"tranche" or "loan-wise".

## 4. SQL safety — layered validation

```mermaid
flowchart TB
    IN["generated SQL"] --> P["parse as MySQL"]
    P --> G1["exactly one statement"]
    G1 --> G2["SELECT only"]
    G2 --> G3["no forbidden keywords"]
    G3 --> G4["inject LIMIT 500"]

    P -.->|unparseable| REJ
    G1 -.->|"stacked statements"| REJ
    G2 -.->|"INSERT, UPDATE, DELETE, DROP"| REJ
    G3 -.->|"INTO OUTFILE, LOAD_FILE"| REJ
    REJ["REJECTED — raises, never reaches the database"]

    G4 --> S1["check_joins"]
    G4 --> S2["check_fanout"]
    G4 --> S3["check_unrequested_filters"]
    G4 --> S4["check_required_predicates"]

    S1 -.->|"hallucinated join"| RES["needs_reselect<br/>back to select_schema"]
    S1 --> OK
    S2 --> OK
    S3 --> OK
    S4 --> OK
    OK["validated_sql<br/>to execute_sql"]

    style REJ fill:#f8e7e3,stroke:#ac3e2e
    style RES fill:#f7eedf,stroke:#8f5e10
    style OK fill:#e2eee9,stroke:#1f6f5c
```

| Check | Looks for |
|---|---|
| `check_joins` | Join conditions that don't exist in the inferred graph |
| `check_fanout` | Junction tables that duplicate rows and inflate counts |
| `check_unrequested_filters` | `WHERE` clauses the question never asked for |
| `check_required_predicates` | Filters the question implies but the SQL omits |

The syntactic guard is absolute — it raises and the query never runs. The four
semantic checks are advisory: they produce a rejection reason that feeds
self-repair rather than an exception.

Belt and suspenders: even if the guard were bypassed entirely, `execute_sql`
runs as `ead_ro`, a MySQL account holding only `GRANT SELECT`, so a write fails
at the server.

## 5. Schema catalog — built once, cached

```mermaid
flowchart LR
    DB[("Analytics DB<br/>MySQL 8.0 / ead_db")] -->|admin_engine| I["introspect<br/>tables, columns, row counts"]
    I --> J["build_join_graph<br/>infer edges from column names"]
    J --> F["measure_fanout<br/>which junctions duplicate rows"]
    I --> V["build_value_index<br/>literal → owning column"]
    J --> W["write JSON"]
    F --> W
    V --> W
    W --> C[(".cache/schema_catalog.json")]
    C -.->|load_catalog| AG["select_schema<br/>validate_sql"]
```

Rebuild with `python scripts/catalog_cli.py --rebuild`. On the bundled dummy
dataset this yields 145 tables, 214 inferred joins, 110 primary keys and 18
isolated tables.

`admin_engine` is the only consumer here, and it never runs generated SQL —
introspection bypasses the guard entirely because it reads schema metadata, not
model output.

## 6. Visualization — heuristics veto, the model only tiebreaks

```mermaid
flowchart TD
    R["result rows"] --> H{"chartable?<br/>2-60 rows,<br/>≥1 numeric + ≥1 categorical column"}
    H -->|no| NONE["chart_spec = none<br/>no image"]
    H -->|yes| L["LLM tiebreak<br/>returns JSON only:<br/>type, x, y, title"]
    L --> SPEC["constrained chart spec<br/>bar | line | pie"]
    SPEC --> RENDER["charts.py renders<br/>plotly + kaleido,<br/>matplotlib fallback"]
    RENDER --> PNG["PNG artifact<br/>owner-scoped"]
    style L fill:#f7eedf,stroke:#8f5e10
```

**The model never sees or writes plotting code.** It returns four fields and
`charts.py` does the drawing, which is what makes chart generation deterministic
and safe.

## 7. State and knobs

`AgentState` is a `TypedDict` threaded through every node.

| Group | Fields |
|---|---|
| input | `question` |
| classify | `verdict`, `reject_reason` |
| select_schema | `candidate_tables`, `selected_tables`, `schema_text`, `join_text`, `value_text` |
| sql | `sql`, `validated_sql`, `columns`, `rows` |
| repair | `error`, `retry_count`, `attempts`, `banned_tables`, `needs_reselect` |
| chart | `chart_spec`, `chart_path`, `chart_figure` |
| output | `answer`, `failed` |

`attempts` is an audit trail of every try, so a run that repaired twice records
all three statements and both rejection reasons.

| Setting | Default | Effect |
|---|---|---|
| `MAX_RETRIES` | 3 | Shared budget across guard rejections and database errors |
| `ROW_LIMIT` | 500 | `LIMIT` injected into every validated statement |
| `QUERY_TIMEOUT_SECONDS` | 30 | Read timeout on the analytics connection |
| `TOP_K_TABLES` | 25 | Candidates from retrieval before the refine call |
| `EMBED_PROVIDER` | `huggingface` | `lexical` short-circuits retrieval to keyword scoring, no model needed |

## 8. Where the LLM is used, and where it is not

Four model calls per successful run, each narrow.

| Node | Model does | Model does **not** |
|---|---|---|
| `classify` | Judge scope: answerable / irrelevant / write_request | Decide what the answer is |
| `select_schema` | Pick 3-8 tables from 25 candidates | Write join conditions — the graph walk does that |
| `generate_sql` | Write one MySQL SELECT | Execute anything |
| `decide_visualization` | Choose chart type and axes | Write plotting code |
| `summarize` | Phrase the answer from returned rows | Introduce any number not in the result table |

Everything structural — joins, LIMIT injection, fan-out detection, chart
rendering, the read-only credential — is deterministic code. That division is
the design, not an implementation detail.

See also: [system-architecture.md](system-architecture.md) for system context and
trust zones, and [fastapi-architecture.md](fastapi-architecture.md) for the API
that calls this package.
