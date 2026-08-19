"""Run the vetted SQL as the read-only user.

Errors are captured into state (not raised) so the graph can route back to
generate_sql for self-repair with the database's own message as the hint --
grounded feedback beats asking the model to guess what went wrong.
"""
from __future__ import annotations

from ead_agent.db import run_readonly
from ead_agent.state import AgentState


def _clean_db_error(msg: str) -> str:
    """Trim SQLAlchemy's wrapper down to the part the model can act on."""
    msg = msg.split("[SQL:")[0]
    msg = msg.replace("(pymysql.err.OperationalError)", "").strip()
    msg = msg.replace("(pymysql.err.ProgrammingError)", "").strip()
    return " ".join(msg.split())[:400]


def execute_sql_node(state: AgentState) -> AgentState:
    sql = state.get("validated_sql") or ""
    if not sql:
        return {**state, "error": state.get("error") or "No SQL to execute."}

    try:
        columns, rows = run_readonly(sql)
    except Exception as e:
        return {
            **state,
            "error": f"Database rejected the query: {_clean_db_error(str(e))}",
            "columns": [],
            "rows": [],
        }

    attempts = list(state.get("attempts", []))
    attempts.append({"sql": sql, "outcome": f"ok ({len(rows)} rows)"})

    return {
        **state,
        "columns": columns,
        "rows": rows,
        "error": None,
        "attempts": attempts,
    }
