"""Typed state passed between graph nodes."""
from __future__ import annotations

from typing import Any, Literal, TypedDict


class ChartSpec(TypedDict, total=False):
    type: Literal["bar", "line", "pie", "none"]
    x: str
    y: str
    title: str
    reason: str


class AgentState(TypedDict, total=False):
    # input
    question: str

    # classify (scope gate, runs before anything else)
    verdict: Literal["answerable", "irrelevant", "write_request"]
    reject_reason: str

    # select_schema
    candidate_tables: list[str]      # top-K from the retriever
    selected_tables: list[str]       # final set, junctions included
    schema_text: str                 # DDL handed to generate_sql
    join_text: str                   # inferred ON clauses
    value_text: str                  # literals in the question -> owning column

    # generate_sql -> validate_sql -> execute_sql
    sql: str
    validated_sql: str               # post-guard (LIMIT injected)
    columns: list[str]
    rows: list[tuple[Any, ...]]
    error: str | None                # last failure, fed back for self-repair
    retry_count: int
    attempts: list[dict[str, str]]   # audit trail of every try
    banned_tables: list[str]         # tables whose keys failed to join
    needs_reselect: bool             # route repair to select_schema, not generate_sql

    # visualization
    chart_spec: ChartSpec | None
    chart_path: str | None
    chart_figure: Any                # plotly Figure for the Gradio UI

    # output
    answer: str
    failed: bool
