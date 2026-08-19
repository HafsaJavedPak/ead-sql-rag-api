"""Deterministic chart rendering.

The model emits a SPEC ({type, x, y, title}) and nothing else. This module is
the only thing that draws. No model-authored plotting code is ever executed --
that would be arbitrary code execution dressed up as a feature.

Plotly builds figures and Kaleido renders protected PNG artifacts.
"""
from __future__ import annotations

import re
import uuid
from typing import Any

import pandas as pd

from ead_agent.config import settings

# Stable application palette for deterministic chart artifacts.
ACCENT = "#d97757"
ACCENT_2 = "#7d94ab"        # muted slate-blue, for a second series
PIE_COLORS = ["#d97757", "#7d94ab", "#c4633f", "#a3a094", "#e0a07f", "#6e6d66"]

MAX_BARS = 30
MAX_PIE_SLICES = 8


def to_dataframe(columns: list[str], rows: list[tuple[Any, ...]]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=columns)
    # Money/count columns often arrive as Decimal or str; coerce where sensible.
    for c in df.columns:
        if df[c].dtype == object:
            converted = pd.to_numeric(df[c], errors="coerce")
            if converted.notna().mean() > 0.8:
                df[c] = converted
    return df


def numeric_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]


def categorical_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]


def _pretty(label: str) -> str:
    out = re.sub(r"_", " ", str(label)).strip()
    out = re.sub(r"\busd mn\b", "USD mn", out, flags=re.I)
    out = re.sub(r"\busd\b", "USD", out, flags=re.I)
    out = re.sub(r"\bpkr\b", "PKR", out, flags=re.I)
    return out[:1].upper() + out[1:]


def render_plotly(spec: dict[str, Any], df: pd.DataFrame):
    """Return a plotly Figure, or None if the spec cannot be honoured."""
    import plotly.graph_objects as go

    ctype, x, y = spec.get("type"), spec.get("x"), spec.get("y")
    if ctype in (None, "none") or x not in df.columns or y not in df.columns:
        return None

    d = df[[x, y]].dropna()
    if d.empty:
        return None

    title = spec.get("title") or f"{_pretty(y)} by {_pretty(x)}"

    if ctype == "bar":
        d = d.head(MAX_BARS)
        fig = go.Figure(go.Bar(x=d[x].astype(str), y=d[y], marker_color=ACCENT))
    elif ctype == "line":
        fig = go.Figure(
            go.Scatter(
                x=d[x].astype(str), y=d[y], mode="lines+markers",
                line=dict(color=ACCENT, width=2.5), marker=dict(size=7),
            )
        )
    elif ctype == "pie":
        d = d[d[y] > 0].head(MAX_PIE_SLICES)
        if d.empty:
            return None
        fig = go.Figure(
            go.Pie(
                labels=d[x].astype(str), values=d[y], hole=0.45,
                marker=dict(colors=PIE_COLORS * 3),
            )
        )
    else:
        return None

    fig.update_layout(
        title=dict(text=title, x=0.02, xanchor="left", font=dict(size=15)),
        margin=dict(l=50, r=25, t=55, b=90),
        height=420,
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=(ctype == "pie"),
    )
    if ctype != "pie":
        fig.update_xaxes(title_text=_pretty(x), tickangle=-35, showgrid=False,
                         linecolor="#D1D5DB")
        fig.update_yaxes(title_text=_pretty(y), gridcolor="#EEF0F3", zeroline=False)
    return fig


def render_png(spec: dict[str, Any], df: pd.DataFrame) -> str | None:
    """Write a chart PNG and return its path.

    Plotly + kaleido first, matplotlib second. Both are attempted because
    either can be unavailable: on this Windows host an Application Control
    policy blocks matplotlib's compiled `_path` DLL entirely, so a
    matplotlib-only path would take the whole app down at import time.
    """
    import uuid as _uuid

    settings.charts_dir.mkdir(parents=True, exist_ok=True)

    try:
        fig = render_plotly(spec, df)
        if fig is not None:
            path = settings.charts_dir / f"chart_{_uuid.uuid4().hex[:12]}.png"
            fig.write_image(str(path), width=900, height=470, scale=2)
            return str(path)
    except Exception:
        pass

    try:
        return render_matplotlib(spec, df)
    except Exception:
        return None


def render_matplotlib(spec: dict[str, Any], df: pd.DataFrame) -> str | None:
    """Fallback renderer. Writes a PNG and returns its path."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ctype, x, y = spec.get("type"), spec.get("x"), spec.get("y")
    if ctype in (None, "none") or x not in df.columns or y not in df.columns:
        return None
    d = df[[x, y]].dropna()
    if d.empty:
        return None

    settings.charts_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4.5))

    if ctype == "bar":
        d = d.head(MAX_BARS)
        ax.bar(d[x].astype(str), d[y], color=ACCENT)
    elif ctype == "line":
        ax.plot(d[x].astype(str), d[y], marker="o", color=ACCENT, linewidth=2.2)
    elif ctype == "pie":
        d = d[d[y] > 0].head(MAX_PIE_SLICES)
        if d.empty:
            plt.close(fig)
            return None
        ax.pie(d[y], labels=d[x].astype(str), autopct="%1.1f%%",
               colors=PIE_COLORS * 3)
        ax.axis("equal")
    else:
        plt.close(fig)
        return None

    if ctype != "pie":
        ax.set_xlabel(_pretty(x))
        ax.set_ylabel(_pretty(y))
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#EEF0F3")
        ax.set_axisbelow(True)
        plt.setp(ax.get_xticklabels(), rotation=35, ha="right")

    ax.set_title(spec.get("title") or f"{_pretty(y)} by {_pretty(x)}", loc="left")
    fig.tight_layout()
    path = settings.charts_dir / f"chart_{uuid.uuid4().hex[:12]}.png"
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return str(path)
