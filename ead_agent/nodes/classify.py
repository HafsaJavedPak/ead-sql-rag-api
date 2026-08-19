"""Relevance gate -- runs BEFORE any SQL is generated.

Without this the agent tries to answer anything. Ask it for the weather and it
will invent a query, or at best return an unrelated table. Ask it to delete a
row and it will attempt SQL that the downstream guard then rejects with a
confusing message.

So questions are classified first, against the ACTUAL schema, into:

    answerable    -- a read-only SELECT over these tables can answer it
    irrelevant    -- general knowledge, small talk, anything not in the data
    write_request -- asks to INSERT/UPDATE/DELETE/ALTER/DROP

Only `answerable` continues to select_schema -> generate_sql. The other two
short-circuit straight to a refusal, so out-of-scope questions never reach the
SQL generation stage at all.

This is a scope gate, not a security control. Writes are still independently
blocked by the sqlglot guard in validate_sql AND by the read-only database
grant; this layer exists so the user gets a clear answer instead of a
confusing SQL error.
"""

import re

from langchain_core.runnables import RunnableConfig

from ead_agent.llm import chat_json
from ead_agent.retriever import top_k_tables
from ead_agent.schema_catalog import load_catalog
from ead_agent.state import AgentState

REFUSAL = "Sorry, I cannot answer this question."

# Unambiguous write intent. Deliberately narrow: these patterns require the
# verb to be followed by something that makes it a command, so ordinary
# read questions are not caught. "Show me recently updated projects" and
# "which projects were dropped from the plan" must both still pass.
WRITE_INTENT = re.compile(
    r"\b("
    r"delete\s+(?:all|every|the|from|rows?|records?|entries)|"
    r"drop\s+(?:the\s+)?(?:table|column|database|schema|index)|"
    r"truncate\b|"
    r"insert\s+(?:a\s+|new\s+|into\b)|"
    r"add\s+(?:a\s+)?(?:new\s+)?(?:row|record|column|table|entry)|"
    r"update\s+(?:the\s+|all\s+)?(?:row|record|table|column|status|value|field)|"
    r"set\s+(?:the\s+)?\w+\s*=|"
    r"alter\s+(?:the\s+)?(?:table|column|schema)|"
    r"create\s+(?:a\s+)?(?:new\s+)?(?:table|column|database|index)|"
    r"rename\s+(?:the\s+)?(?:table|column)|"
    r"remove\s+(?:the\s+)?(?:row|record|column|table)\b"
    r")",
    re.I,
)

SYSTEM = """You are a scope checker for a text-to-SQL assistant that serves
Pakistan's Economic Affairs Division (EAD). It answers questions about foreign
economic assistance by running READ-ONLY SELECT queries.

Given a user's question and the tables available, classify it as exactly one of:

  "answerable"    - the question asks for information that a SELECT over these
                    tables could plausibly return (counts, totals, lists,
                    comparisons, trends about projects, donors, sectors,
                    disbursements, regions, agencies, courses, debt, etc.)
  "irrelevant"    - the question is not about this data at all: general
                    knowledge, weather, news, maths, coding help, greetings,
                    small talk, questions about you, or any other database.
  "write_request" - the question asks to CHANGE data or structure: insert,
                    add, update, edit, set, delete, remove, drop, truncate,
                    alter, rename, create a table.

Rules:
- Judge INTENT, not keywords. "Show projects updated this year" is answerable
  (it reads). "Update project 5" is a write_request.
- If the question is about the EAD domain but the exact field may not exist,
  still answer "answerable" -- the SQL stage will handle it.
- Vague but on-topic questions ("show me the data", "top donors") are
  "answerable".
- A question mixing both ("list projects and delete the old ones") is
  "write_request".

Return JSON: {"verdict": "...", "reason": "<max 12 words>"}"""


def _table_hint(names: list[str], catalog: dict, limit: int = 18) -> str:
    lines = []
    for n in names[:limit]:
        t = catalog["tables"].get(n)
        if t:
            lines.append(f"- {n}: {t['description'][:88]}")
    return "\n".join(lines)


def classify_question_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    question = (state.get("question") or "").strip()

    if not question:
        return {**state, "verdict": "irrelevant", "reject_reason": "empty question"}

    # 1. Deterministic write-intent check. Runs first and is not delegated to
    #    the model, so an LLM outage cannot let a write request through.
    if WRITE_INTENT.search(question):
        return {
            **state,
            "verdict": "write_request",
            "reject_reason": "asks to modify data or schema",
        }

    # 2. Model classification, grounded in the tables the retriever surfaces
    #    for this question -- so "relevance" is judged against the real schema
    #    rather than the model's idea of what EAD might hold.
    try:
        catalog = load_catalog()
        candidates = [n for n, _ in top_k_tables(question, 18)]
        hint = _table_hint(candidates, catalog)
        got = chat_json(
            SYSTEM,
            f"QUESTION: {question}\n\nTABLES AVAILABLE (sample):\n{hint}",
            config=config,
            run_name="agent.classify",
        )
        verdict = str(got.get("verdict", "")).strip().lower()
        reason = str(got.get("reason", ""))[:120]
    except Exception:
        # Fail OPEN on a classifier error: the write guard above already ran,
        # and validate_sql plus the read-only grant still protect the database.
        # Refusing everything because of a transient API blip would be worse.
        return {**state, "verdict": "answerable", "reject_reason": "classifier unavailable"}

    if verdict not in {"answerable", "irrelevant", "write_request"}:
        verdict = "answerable"

    return {**state, "verdict": verdict, "reject_reason": reason}


def refuse_node(state: AgentState) -> AgentState:
    """Terminal node for out-of-scope questions. No SQL was generated."""
    return {
        **state,
        "answer": REFUSAL,
        "failed": True,
        "sql": "",
        "validated_sql": "",
        "columns": [],
        "rows": [],
        "chart_spec": {"type": "none", "reason": "question out of scope"},
        "selected_tables": [],
    }
