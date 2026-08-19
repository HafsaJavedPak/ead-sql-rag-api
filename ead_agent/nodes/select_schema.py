"""Pick the handful of tables relevant to the question.

146 tables x ~9 columns will not fit in a prompt, and stuffing them in would
bury the signal even if it did. Three stages:

    1. retrieve  -- embeddings + lexical, top-K candidates
    2. refine    -- one cheap LLM call picks the final 3-8
    3. connect   -- deterministic join-graph walk adds the junction tables the
                    model forgot. This step is NOT delegated to the model:
                    with one FK in the whole schema, a hallucinated join
                    condition is the most likely way to get a wrong answer
                    that still executes.
"""

from langchain_core.runnables import RunnableConfig

from ead_agent.llm import chat_json
from ead_agent.retriever import top_k_tables
from ead_agent.schema_catalog import connect_tables, join_hints, load_catalog, match_values
from ead_agent.state import AgentState

MAX_FINAL_TABLES = 8

# Canonical vs look-alike tables. Both retrieval and the model confuse these
# structurally-similar pairs, picking the smaller sub-detail table and
# undercounting. Steer to the canonical one unless the question explicitly
# asks for the detail/pipeline variant (trigger words).
#   look-alike : (canonical, trigger words that justify the look-alike)
CANONICAL_PREFERENCE = {
    "project_to_foreigndetails": (
        "project_to_foreigncecomponents",
        (
            "tranche",
            "sub-loan",
            "subloan",
            "sub loan",
            "loan detail",
            "grant detail",
            "loan-wise",
            "grant-wise",
            "foreign detail",
            "individual loan",
            "individual grant",
        ),
    ),
    "wq_piplineprojects": (
        "project_to_financials",
        (
            "pipeline",
            "pipline",
            "planned project",
            "upcoming project",
            "planned projects",
            "upcoming projects",
            "in the pipeline",
        ),
    ),
}

SYSTEM = """You select database tables for a text-to-SQL system serving
Pakistan's Economic Affairs Division (EAD), which tracks foreign economic
assistance: donors, projects, disbursements, debt and off-budget programmes.

You are given a question and candidate tables. Choose ONLY the tables needed
to answer it. Prefer master tables prefixed `wq_` plus the `*_to_*` junction
tables that connect them. Fewer is better; never exceed 8.

Canonical links (use these, not their look-alikes):
- donor <-> project funding  -> project_to_foreigncecomponents
- project cost / spend       -> project_to_financials
Do not add a junction table you do not actually need to answer the question.

Return JSON: {"tables": ["...", "..."], "reason": "one sentence"}"""


def _apply_canonical(question: str, candidates: list[str], catalog: dict):
    """Drop look-alike tables from the candidate list (unless the question
    triggers them) and guarantee their canonical counterpart is present.
    Returns (new_candidates, notes)."""
    q = question.lower()
    out = list(candidates)
    notes = []
    for lookalike, (canonical, triggers) in CANONICAL_PREFERENCE.items():
        if lookalike not in out:
            continue
        if any(t in q for t in triggers):
            continue  # question genuinely wants the detail/pipeline table
        out = [t for t in out if t != lookalike]
        if canonical in catalog["tables"] and canonical not in out:
            out.insert(0, canonical)
        notes.append(f"Use `{canonical}` for this, NOT `{lookalike}`.")
    return out, notes


def _candidate_block(catalog: dict, names: list[str]) -> str:
    lines = []
    for n in names:
        t = catalog["tables"][n]
        cols = ", ".join(c["name"] for c in t["columns"][:14])
        lines.append(f"- {n} ({t['row_count']:,} rows): {t['description']}\n    columns: {cols}")
    return "\n".join(lines)


def select_schema_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    question = state["question"]
    catalog = load_catalog()

    # Tables proven unusable on a previous pass (their keys did not join).
    banned = set(state.get("banned_tables", []))

    ranked = top_k_tables(question)
    candidates = [n for n, _ in ranked if n not in banned]

    # Steer away from look-alike tables (foreigndetails, piplineprojects)
    # toward their canonical counterparts unless the question asks otherwise.
    candidates, canonical_notes = _apply_canonical(question, candidates, catalog)

    # Ground literal values BEFORE the model picks tables. Retrieval ranks on
    # descriptions, so "active projects in Punjab" surfaced sector tables and
    # the model then filtered sectors instead of regions. Telling it up front
    # that "Punjab" lives in wq_regions.region_name fixes the choice at source.
    value_hits = match_values(question, catalog.get("value_index") or {})
    value_lines = [f'  "{v}" is a value of `{ref}`' for v, ref in value_hits]
    value_text = "\n".join(dict.fromkeys(value_lines))

    user = (
        f"QUESTION: {question}\n\nCANDIDATE TABLES:\n"
        f"{_candidate_block(catalog, candidates)}\n\n"
        + (
            "VALUES NAMED IN THE QUESTION (verified against the data -- the "
            "table holding each value MUST be included):\n" + value_text + "\n\n"
            if value_text
            else ""
        )
        + (
            "CANONICAL TABLE GUIDANCE:\n  " + "\n  ".join(canonical_notes) + "\n\n"
            if canonical_notes
            else ""
        )
        + (
            f"Do NOT use these tables, a previous attempt showed their keys do "
            f"not join here: {', '.join(sorted(banned))}.\n\n"
            if banned
            else ""
        )
        + "Which tables are needed?"
    )
    try:
        picked = (
            chat_json(
                SYSTEM,
                user,
                config=config,
                run_name="agent.select-schema",
            ).get("tables")
            or []
        )
    except Exception:
        picked = []

    # Keep only real tables; fall back to the retriever's top hits if the
    # model returned nothing usable.
    picked = [t for t in picked if t in catalog["tables"] and t not in banned][:MAX_FINAL_TABLES]
    if not picked:
        picked = candidates[:4]

    # Deterministic bridging, biased toward the retrieved domain.
    selected = connect_tables(
        picked,
        catalog["join_graph"]["adjacency"],
        max_hops=2,
        preferred=set(candidates),
    )[: MAX_FINAL_TABLES + 4]

    # Then pull in the lookup tables the selected tables point at.
    selected = _add_lookups(selected, catalog)

    # Make sure the table holding each named value is actually in the set, and
    # that it is reachable -- adding wq_regions alone is not enough if nothing
    # selected joins to it, which is how the model ended up inventing
    # `projectsector_name = region_name`.
    for _val, ref in value_hits:
        tbl = ref.split(".")[0]
        if tbl not in selected:
            selected = connect_tables(
                selected + [tbl],
                catalog["join_graph"]["adjacency"],
                max_hops=2,
                preferred=set(candidates) | {tbl},
            )

    # A look-alike must not survive via bridging either, unless triggered.
    q_low = question.lower()
    for lookalike, (_canonical, triggers) in CANONICAL_PREFERENCE.items():
        if lookalike in selected and not any(t in q_low for t in triggers):
            selected = [t for t in selected if t != lookalike]

    tables = catalog["tables"]
    schema_text = "\n\n".join(_ddl(tables[t]) for t in selected if t in tables)
    hints = join_hints(selected, catalog["join_graph"])
    join_text = "\n".join(f"  {h}" for h in hints) or "  (no inferred joins between these tables)"

    return {
        **state,
        "candidate_tables": candidates,
        "selected_tables": selected,
        "schema_text": schema_text,
        "join_text": join_text,
        "value_text": value_text,
        "needs_reselect": False,
    }


# Lookup tables are small by nature (regions, sectors, statuses, currencies).
# The bound keeps this from dragging in a large fact table by accident.
LOOKUP_MAX_ROWS = 2000
MAX_LOOKUPS = 5


def _add_lookups(selected: list[str], catalog: dict) -> list[str]:
    """Add the master table behind each `*_id` column of the selected tables.

    Retrieval matches on table DESCRIPTIONS, so a question naming a specific
    VALUE has nothing to match on: "active projects in Balochistan" never
    surfaced `wq_regions`, because nothing in that table's description looks
    like the word "Balochistan". The model was then handed
    project_to_executingencies with a region_id it could not resolve to a
    name, and filtered on `pd_name` -- the project DIRECTOR's name -- instead,
    silently returning 0 where the true answer was 13.

    So whenever a table with a foreign key is selected, its lookup table comes
    too. That is what makes the id resolvable to a human-readable name.
    """
    tables = catalog["tables"]
    pk_index = catalog["join_graph"]["pk_index"]

    out = list(selected)
    added = 0
    for tname in selected:
        t = tables.get(tname)
        if not t:
            continue
        own_pk = set(t["primary_key"])
        for col in t["columns"]:
            if added >= MAX_LOOKUPS:
                return out
            name = col["name"]
            if not name.endswith("_id") or name in own_pk:
                continue
            target = pk_index.get(name)
            if not target or target in out:
                continue
            tgt = tables.get(target)
            if not tgt or tgt["row_count"] > LOOKUP_MAX_ROWS:
                continue
            out.append(target)
            added += 1
    return out


def _ddl(t: dict) -> str:
    lines = [f"CREATE TABLE `{t['name']}` ("]
    for c in t["columns"]:
        line = f"  `{c['name']}` {c['data_type']}"
        if c["is_pk"]:
            line += " PRIMARY KEY"
        if c["comment"]:
            line += f"  -- {c['comment']}"
        lines.append(line + ",")
    lines.append(f")  -- {t['description']} ({t['row_count']:,} rows)")
    return "\n".join(lines)
