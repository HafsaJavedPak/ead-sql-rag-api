"""Question + selected schema + domain rules -> one MySQL SELECT.

On a retry the previous SQL and the exact database error are appended, so the
model repairs against real feedback instead of guessing.
"""

from langchain_core.runnables import RunnableConfig

from ead_agent.domain import DOMAIN_NOTES
from ead_agent.few_shots import render as render_few_shots
from ead_agent.llm import chat
from ead_agent.state import AgentState

SYSTEM = f"""You write MySQL SELECT queries for Pakistan's Economic Affairs
Division (EAD) foreign-assistance database.

RULES
- Output ONE MySQL SELECT statement. No prose, no markdown fences, no semicolon.
- Read-only. Never INSERT/UPDATE/DELETE/DROP/ALTER/CREATE.
- Use ONLY the tables and columns given to you. Never invent a column.
- Use the supplied join conditions verbatim -- this schema has almost no
  foreign keys, so a guessed join will silently return wrong numbers.
- Alias tables, qualify every column, and give computed columns clear names.
- Backtick-quote identifiers that are reserved words (`from`, `to`).
- Add a sensible LIMIT for list-style questions.
- Prefer human-readable labels over raw status codes.

{DOMAIN_NOTES}

WORKED EXAMPLES
{render_few_shots()}
"""


def generate_sql_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    parts = [
        f"QUESTION: {state['question']}",
        "",
        "AVAILABLE TABLES:",
        state.get("schema_text", ""),
        "",
        "VERIFIED JOIN CONDITIONS (use these exactly):",
        state.get("join_text", ""),
    ]

    # Literal values in the question, resolved to the column that holds them.
    # Looked up in the real data, so filter on exactly these columns rather
    # than guessing which table a name belongs to.
    value_text = state.get("value_text") or ""
    if value_text:
        parts += [
            "",
            "VALUES NAMED IN THE QUESTION (verified against the data --",
            "filter on THESE columns, do not guess another table):",
            value_text,
        ]

    prev_error = state.get("error")
    if prev_error:
        parts += [
            "",
            "YOUR PREVIOUS ATTEMPT FAILED.",
            f"SQL you wrote:\n{state.get('sql', '')}",
            f"Failure: {prev_error}",
            "Fix the specific problem. Do not repeat the same query.",
        ]

    sql = chat(
        SYSTEM,
        "\n".join(parts),
        temperature=0.0,
        max_tokens=900,
        config=config,
        run_name="agent.generate-sql",
    )

    attempts = list(state.get("attempts", []))
    if prev_error:
        attempts.append({"sql": state.get("sql", ""), "outcome": prev_error})

    return {**state, "sql": sql, "attempts": attempts}
