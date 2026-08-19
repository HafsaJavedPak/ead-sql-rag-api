"""Decide whether a chart helps, then render it deterministically.

Heuristics decide first and can veto outright; the LLM is only a tiebreaker
for bar-vs-line-vs-pie once the shape is known to be chartable. The model
never sees or writes plotting code -- it returns {type, x, y, title} and
charts.py does the drawing.
"""

import pandas as pd
from langchain_core.runnables import RunnableConfig

from ead_agent.charts import (
    categorical_columns,
    numeric_columns,
    render_png,
    to_dataframe,
)
from ead_agent.llm import chat_json
from ead_agent.state import AgentState

MIN_ROWS = 2
MAX_ROWS = 60

SYSTEM = """You choose a chart type for a query result. Reply JSON only:
{"type": "bar|line|pie|none", "x": "<column>", "y": "<column>", "title": "<short title>"}

Guidance:
- line  : the x axis is ordered time (fiscal years, dates, months)
- bar   : comparing a measure across categories
- pie   : parts of one whole, at most 8 slices, no negatives
- none  : the result is not worth charting
Use exact column names from the list given."""


def _heuristic(df: pd.DataFrame) -> dict | None:
    """Return a veto ({'type':'none'}) or a suggestion, or None for 'ask the LLM'."""
    if df.empty or len(df) < MIN_ROWS:
        return {"type": "none", "reason": "fewer than 2 rows"}
    if len(df) > MAX_ROWS:
        return {"type": "none", "reason": f"{len(df)} rows is too many to chart"}
    nums = numeric_columns(df)
    cats = categorical_columns(df)
    if not nums:
        return {"type": "none", "reason": "no numeric column to plot"}
    if not cats and len(nums) < 2:
        return {"type": "none", "reason": "nothing to plot against"}
    return None


def _looks_temporal(name: str, series: pd.Series) -> bool:
    n = name.lower()
    if any(k in n for k in ("year", "fiscal", "month", "date", "period", "quarter")):
        return True
    return pd.api.types.is_datetime64_any_dtype(series)


def decide_visualization_node(
    state: AgentState, config: RunnableConfig | None = None
) -> AgentState:
    columns = state.get("columns") or []
    rows = state.get("rows") or []
    if not columns or not rows:
        return {**state, "chart_spec": {"type": "none", "reason": "no result rows"}}

    df = to_dataframe(columns, rows)
    veto = _heuristic(df)
    if veto is not None:
        return {**state, "chart_spec": veto}

    nums = numeric_columns(df)
    cats = categorical_columns(df)
    x_default = cats[0] if cats else df.columns[0]
    y_default = nums[0]

    # Strong heuristic: an ordered time axis is a line chart, no call needed.
    if _looks_temporal(x_default, df[x_default]):
        spec = {
            "type": "line",
            "x": x_default,
            "y": y_default,
            "title": (
                f"{y_default.replace('_', ' ').title()} by {x_default.replace('_', ' ').title()}"
            ),
            "reason": "ordered time axis",
        }
    else:
        try:
            got = chat_json(
                SYSTEM,
                f"Question: {state['question']}\n"
                f"Columns: {list(df.columns)}\n"
                f"Row count: {len(df)}\n"
                f"First rows:\n{df.head(5).to_string(index=False)}",
                config=config,
                run_name="agent.decide-visualization",
            )
        except Exception:
            got = {}
        spec = {
            "type": got.get("type", "bar"),
            "x": got.get("x", x_default),
            "y": got.get("y", y_default),
            "title": got.get("title", ""),
            "reason": "model choice",
        }

    # The model can name a column that isn't there; fall back rather than fail.
    if spec.get("x") not in df.columns:
        spec["x"] = x_default
    if spec.get("y") not in df.columns or spec["y"] not in nums:
        spec["y"] = y_default

    return {**state, "chart_spec": spec}


def render_chart_node(state: AgentState) -> AgentState:
    spec = state.get("chart_spec") or {}
    if spec.get("type") in (None, "none"):
        return {**state, "chart_figure": None, "chart_path": None}

    df = to_dataframe(state.get("columns", []), state.get("rows", []))
    try:
        path = render_png(spec, df)
    except Exception:
        path = None
    return {**state, "chart_figure": None, "chart_path": path}
