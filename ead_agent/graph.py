"""LangGraph assembly.

    classify -+-(irrelevant | write_request)-> refuse -> END
              |
              +-(answerable)-> select_schema -> generate_sql -> validate_sql -> execute_sql
                                     ^               |               |
                                     |          (rejected)       (db error)
                                     +---------------+---------------+
                                               retry_count < MAX_RETRIES
                                                     else -> fail

    execute_sql -ok-> decide_visualization -> render_chart -> summarize -> END

Both failure kinds (guard rejection and database error) feed the same repair
edge and share one counter, so a query that is rejected twice then errors once
still stops at MAX_RETRIES total.
"""

from __future__ import annotations

from typing import Literal

from langgraph.graph import END, StateGraph

from ead_agent.config import settings
from ead_agent.nodes import (
    classify_question_node,
    decide_visualization_node,
    execute_sql_node,
    fail_node,
    generate_sql_node,
    refuse_node,
    render_chart_node,
    select_schema_node,
    summarize_node,
    validate_sql_node,
)
from ead_agent.state import AgentState


def _bump_retry(state: AgentState) -> AgentState:
    return {**state, "retry_count": state.get("retry_count", 0) + 1}


def _after_validate(state: AgentState) -> Literal["execute", "reselect", "retry", "fail"]:
    if not state.get("error"):
        return "execute"
    if state.get("retry_count", 0) >= settings.max_retries:
        return "fail"
    # A hallucinated join means the wrong TABLE was chosen. Regenerating SQL
    # against the same table set reproduces the same bad join, so go back to
    # schema selection with the offending table excluded.
    if state.get("needs_reselect"):
        return "reselect"
    return "retry"


def _after_execute(state: AgentState) -> Literal["visualize", "retry", "fail"]:
    if not state.get("error"):
        return "visualize"
    return "retry" if state.get("retry_count", 0) < settings.max_retries else "fail"


def _after_classify(state: AgentState) -> Literal["proceed", "refuse"]:
    """Scope gate. Only `answerable` questions reach SQL generation."""
    return "proceed" if state.get("verdict") == "answerable" else "refuse"


def build_graph(*, checkpointer=None, include_summary: bool = True):
    g = StateGraph(AgentState)

    g.add_node("classify", classify_question_node)
    g.add_node("refuse", refuse_node)
    g.add_node("select_schema", select_schema_node)
    g.add_node("generate_sql", generate_sql_node)
    g.add_node("validate_sql", validate_sql_node)
    g.add_node("execute_sql", execute_sql_node)
    g.add_node("bump_retry", _bump_retry)
    g.add_node("decide_visualization", decide_visualization_node)
    g.add_node("render_chart", render_chart_node)
    g.add_node("summarize", summarize_node)
    g.add_node("fail", fail_node)

    # Scope gate first: an irrelevant or write-intent question ends at `refuse`
    # having generated no SQL and touched no table.
    g.set_entry_point("classify")
    g.add_conditional_edges(
        "classify",
        _after_classify,
        {"proceed": "select_schema", "refuse": "refuse"},
    )
    g.add_edge("refuse", END)

    g.add_edge("select_schema", "generate_sql")
    g.add_edge("generate_sql", "validate_sql")

    g.add_node("bump_and_reselect", _bump_retry)

    g.add_conditional_edges(
        "validate_sql",
        _after_validate,
        {
            "execute": "execute_sql",
            "reselect": "bump_and_reselect",
            "retry": "bump_retry",
            "fail": "fail",
        },
    )
    # Re-selection edge: same retry budget, but re-enters at schema selection.
    g.add_edge("bump_and_reselect", "select_schema")
    g.add_conditional_edges(
        "execute_sql",
        _after_execute,
        {"visualize": "decide_visualization", "retry": "bump_retry", "fail": "fail"},
    )

    # The single repair edge: increment, then regenerate with the error in hand.
    g.add_edge("bump_retry", "generate_sql")

    g.add_edge("decide_visualization", "render_chart")
    if include_summary:
        g.add_edge("render_chart", "summarize")
        g.add_edge("summarize", END)
    else:
        g.add_edge("render_chart", END)
    g.add_edge("fail", END)

    return g.compile(checkpointer=checkpointer)
