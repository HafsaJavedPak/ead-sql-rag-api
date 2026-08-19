"""Two or three sentences grounded in the rows that were actually returned.

The model is given the real result table and told not to introduce any number
that is not in it. This is the one node that sends result DATA (not just
schema) to the LLM -- see the privacy note in README.md.
"""

from collections.abc import AsyncIterator

from langchain_core.runnables import RunnableConfig

from ead_agent.charts import to_dataframe
from ead_agent.llm import astream_chat, chat
from ead_agent.state import AgentState

MAX_ROWS_IN_PROMPT = 30

SYSTEM = """You answer data questions for staff at Pakistan's Economic Affairs
Division. Most readers are not analysts, so write for a general audience.

GROUNDING -- this matters more than style
- Use ONLY numbers and names present in the result table. Never estimate,
  extrapolate, or infer a cause.
- Never add a filler sentence to reach a length. If the result is one number,
  one sentence is the correct and complete answer. Padding with vague context
  ("various initiatives across sectors") is a factual error, not a flourish.
- Quote figures with their units as labelled (a column ending _usd_mn is
  millions of USD). If a column is named 'projected', say projected -- do not
  call it disbursed or spent.

STYLE
- Open with the direct answer to the question, in plain English. No preamble
  like "Based on the data" or "The query returned".
- Write out large numbers readably: 4,930 not 4930; "1.2 billion USD" reads
  better than 1200 millions USD.
- Bold the single headline figure with **asterisks**.
- One number or one fact -> a single sentence.
- A ranking or breakdown of 3+ rows -> one short lead sentence, then a compact
  markdown bullet list of the top items as "- **Name** — value". Do not repeat
  every row that is already visible in the table below your answer.
- Add a second sentence only when it states a real comparison you can read off
  the table (a gap, a share, a tie, a leader).
- Never mention SQL, tables, columns, joins, or the database. The reader wants
  the finding, not how it was retrieved."""


def _summary_input(state: AgentState) -> str:
    columns = state.get("columns") or []
    rows = state.get("rows") or []
    df = to_dataframe(columns, rows)
    shown = df.head(MAX_ROWS_IN_PROMPT)
    more = "" if len(df) <= MAX_ROWS_IN_PROMPT else f"\n(+{len(df) - MAX_ROWS_IN_PROMPT} more rows)"
    return (
        f"Question: {state['question']}\n\n"
        f"Result ({len(df)} rows):\n{shown.to_string(index=False)}{more}"
    )


def summarize_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    if state.get("failed"):
        return state

    rows = state.get("rows") or []
    if not rows:
        return {
            **state,
            "answer": "The query ran successfully but matched no rows.",
        }

    user = _summary_input(state)
    try:
        answer = chat(
            SYSTEM,
            user,
            temperature=0.2,
            max_tokens=260,
            config=config,
            run_name="agent.summarize",
            tags=["assistant-output"],
        )
    except Exception as e:
        answer = f"Returned {len(rows)} rows. (Summary unavailable: {type(e).__name__})"

    return {**state, "answer": answer}


async def stream_summary(
    state: AgentState, config: RunnableConfig | None = None
) -> AsyncIterator[str]:
    """Stream the actual final model generation used as the assistant answer."""
    if state.get("failed"):
        if state.get("answer"):
            yield state["answer"]
        return
    rows = state.get("rows") or []
    if not rows:
        yield "The query ran successfully but matched no rows."
        return
    async for chunk in astream_chat(
        SYSTEM,
        _summary_input(state),
        temperature=0.2,
        max_tokens=260,
        config=config,
        run_name="agent.summarize",
        tags=["assistant-output"],
    ):
        yield chunk


def fail_node(state: AgentState) -> AgentState:
    """Terminal node when self-repair is exhausted. Says what went wrong
    rather than pretending to answer."""
    err = state.get("error") or "unknown error"
    tried = len(state.get("attempts", []))
    return {
        **state,
        "failed": True,
        "answer": (
            f"I could not build a working query for that question after {tried} "
            f"attempt(s). Last problem: {err}\n\n"
            "Try naming the entity you mean (donor, project, sector, fiscal year), "
            "or ask for something narrower."
        ),
    }
