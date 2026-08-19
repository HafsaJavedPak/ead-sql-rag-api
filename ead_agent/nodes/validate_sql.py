"""SELECT-only guard. Runs before anything touches the database.

This is the second of two defences -- the first is that the executing user
holds GRANT SELECT only. Both exist because either alone is a single point of
failure: a misconfigured grant, or a parser bypass.
"""
from __future__ import annotations

import re
from typing import Any

import sqlglot
from sqlglot import exp

from ead_agent.config import settings
from ead_agent.state import AgentState

BANNED = {
    exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create, exp.Alter,
    exp.TruncateTable, exp.Grant,
}

# Statements sqlglot may parse as anonymous commands; catch by keyword too.
#
# Careful with words that are also FUNCTIONS. `REPLACE(str, a, b)` is a normal
# string function -- domain.py actively tells the model to use it to strip
# thousands separators -- while `REPLACE INTO` is a write. Match the statement
# forms only, never the bare word. Same reasoning for the others: they are
# anchored to what actually follows them in a statement.
BANNED_KEYWORDS = re.compile(
    r"\b(?:"
    r"insert\s+(?:into|ignore)|"
    r"replace\s+into|"
    r"update\s+\w|"
    r"delete\s+from|"
    r"drop\s+(?:table|database|schema|view|index|user)|"
    r"alter\s+(?:table|database|schema|view|user)|"
    r"truncate\s+table|"
    r"create\s+(?:table|database|schema|view|index|user|or\s+replace)|"
    r"grant\s+\w|revoke\s+\w|"
    r"rename\s+table|"
    r"load\s+data|into\s+outfile|into\s+dumpfile|"
    r"set\s+global"
    r")\b",
    re.I,
)


class GuardError(Exception):
    pass


def _strip_fences(sql: str) -> str:
    s = sql.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    return s.strip().rstrip(";").strip()


def guard(sql: str) -> str:
    """Return the vetted SQL (with LIMIT injected) or raise GuardError."""
    sql = _strip_fences(sql)
    if not sql:
        raise GuardError("Empty query.")

    try:
        statements = sqlglot.parse(sql, read="mysql")
    except Exception as e:
        raise GuardError(f"Could not parse as MySQL: {e}") from e

    statements = [s for s in statements if s is not None]
    if len(statements) != 1:
        raise GuardError(
            f"Exactly one statement is allowed; found {len(statements)}. "
            "Do not use semicolons to chain queries."
        )

    stmt = statements[0]

    # Must be a SELECT (a bare WITH ... SELECT is fine too).
    if not isinstance(stmt, (exp.Select, exp.Subquery, exp.Union)):
        raise GuardError(
            f"Only SELECT is permitted; got {type(stmt).__name__.upper()}."
        )

    for node in stmt.walk():
        if type(node) in BANNED:
            raise GuardError(
                f"{type(node).__name__.upper()} is not allowed -- this is a read-only agent."
            )

    # Keyword sweep over the literal text. Strip string literals AND comments
    # first: a value like 'Project Update', or an explanatory comment such as
    # "-- drop raw-dollar typos", is not a statement and must not trip the
    # guard. (Both false positives were observed in practice.)
    scrubbed = re.sub(r"'(?:[^']|'')*'", "''", sql)
    scrubbed = re.sub(r"/\*.*?\*/", " ", scrubbed, flags=re.S)   # /* ... */
    scrubbed = re.sub(r"--[^\n]*", " ", scrubbed)                 # -- ...
    scrubbed = re.sub(r"#[^\n]*", " ", scrubbed)                  # MySQL # ...
    m = BANNED_KEYWORDS.search(scrubbed)
    if m:
        raise GuardError(f"Forbidden keyword {m.group(0)!r} in query.")

    return _ensure_limit(stmt)


def _ensure_limit(stmt: exp.Expression) -> str:
    """Inject LIMIT when absent so a stray cross join can't stream the table."""
    if isinstance(stmt, exp.Select) and not stmt.args.get("limit"):
        stmt = stmt.limit(settings.row_limit)
    return stmt.sql(dialect="mysql", pretty=True)


# --------------------------------------------------------------------------
# Join validation -- the schema has ~1 foreign key, so a hallucinated join
# executes happily and returns confident nonsense. Every equality between two
# columns of different tables must exist in the inferred join graph.
# --------------------------------------------------------------------------

def _column_pairs(stmt: exp.Expression) -> list[tuple[str, str]]:
    """Extract (col_a, col_b) for every `x.a = y.b` comparison in the query."""
    pairs = []
    for eq in stmt.find_all(exp.EQ):
        left, right = eq.this, eq.expression
        if isinstance(left, exp.Column) and isinstance(right, exp.Column):
            pairs.append((left.name, right.name))
    return pairs


def check_joins(sql: str, edges: list[dict] | None) -> list[str]:
    """Return a list of suspicious join conditions (empty == fine)."""
    if not edges:
        return []
    known: set[frozenset[str]] = set()
    for e in edges:
        known.add(frozenset((e["from_column"], e["to_column"])))
    # Same-named columns are always acceptable (donor_id = donor_id).
    try:
        stmt = sqlglot.parse_one(sql, read="mysql")
    except Exception:
        return []

    bad = []
    for a, b in _column_pairs(stmt):
        if a == b:
            continue
        if frozenset((a, b)) in known:
            continue
        # Any equality between two DIFFERENTLY-named columns that the join
        # graph does not connect is suspect. Originally this only checked
        # *_id pairs, which let a far worse join through:
        #     JOIN wq_regions r ON s.projectsector_name = r.region_name
        # -- joining a sector name to a region name. Valid SQL, zero rows, and
        # reported as "0 active projects in Punjab" when the answer was 39.
        bad.append(f"{a} = {b}")
    return bad


def validate_sql_node(state: AgentState) -> AgentState:
    try:
        vetted = guard(state.get("sql", ""))
    except GuardError as e:
        return {
            **state,
            "error": f"SQL rejected by safety guard: {e}",
            "validated_sql": "",
        }

    from ead_agent.schema_catalog import load_catalog  # local import avoids a cycle

    try:
        edges = load_catalog()["join_graph"]["edges"]
    except Exception:
        edges = None


    bad = check_joins(vetted, edges)
    if bad:
        # A bogus join usually means the WRONG TABLE was selected, not that the
        # SQL needs rewording -- regenerating against the same table set just
        # reproduces it. Identify the table that owns the offending key so the
        # graph can re-select without it.
        banned = list(state.get("banned_tables", []))
        try:
            pk_index = load_catalog()["join_graph"]["pk_index"]
        except Exception:
            pk_index = {}
        selected = set(state.get("selected_tables", []))
        for cond in bad:
            for col in re.split(r"\s*=\s*", cond):
                owner = pk_index.get(col.strip())
                if owner and owner in selected and owner not in banned:
                    banned.append(owner)

        return {
            **state,
            "validated_sql": "",
            "banned_tables": banned,
            "needs_reselect": bool(banned),
            "error": (
                "Invalid join condition(s): " + "; ".join(bad) + ". "
                "These columns are different keys and are not linked in this "
                "database. Use only the verified join conditions supplied, and "
                "route through the correct junction table."
                + (f" Avoid these tables: {', '.join(banned)}." if banned else "")
            ),
        }

    missing = check_required_predicates(vetted)
    if missing:
        return {**state, "validated_sql": "", "error": "; ".join(missing)}

    try:
        fanout = load_catalog()["join_graph"].get("fanout", {})
    except Exception:
        fanout = {}
    inflated = check_fanout(vetted, fanout)
    if inflated:
        return {**state, "validated_sql": "", "error": "; ".join(inflated)}

    spurious = check_unrequested_filters(vetted, state.get("question", ""))
    if spurious:
        return {**state, "validated_sql": "", "error": "; ".join(spurious)}

    return {**state, "validated_sql": vetted, "error": None}


# --------------------------------------------------------------------------
# Unrequested-filter guard
#
# The model keeps bolting an extra junction onto a simple question and adding
# a filter the user never asked for -- e.g. "projects through the ECNEC forum"
# became ... JOIN project_to_issues WHERE projectissue_status = 1, collapsing
# 111 to 3. Prompt rules did not stop it. So: flag a `*_to_*` junction that is
# used ONLY to filter (none of its columns are selected), whose subject the
# question never mentions, and which is not a value the question named.
# --------------------------------------------------------------------------

_FILTER_OPS = (exp.EQ, exp.NEQ, exp.GT, exp.GTE, exp.LT, exp.LTE, exp.Like, exp.In)


def _table_noun(name: str) -> str:
    stem = name.split("_to_")[-1] if "_to_" in name else name.replace("wq_", "")
    return stem.replace("_", "")


def check_unrequested_filters(sql: str, question: str) -> list[str]:
    try:
        stmt = sqlglot.parse_one(sql, read="mysql")
    except Exception:
        return []

    q = (question or "").lower()
    try:
        from ead_agent.schema_catalog import load_catalog, match_values
        cat = load_catalog()
        grounded = {
            ref.split(".")[0]
            for _v, ref in match_values(question, cat.get("value_index") or {})
        }
    except Exception:
        grounded = set()

    alias2table = {t.alias_or_name: t.name for t in stmt.find_all(exp.Table)}

    # Tables whose columns appear in the SELECT projection (not just WHERE/ON).
    selected_aliases: set[str] = set()
    for sel in stmt.find_all(exp.Select):
        for proj in sel.expressions:                       # projection list only
            for col in proj.find_all(exp.Column):
                if col.table:
                    selected_aliases.add(col.table)

    problems: list[str] = []
    seen: set[str] = set()
    scopes = list(stmt.find_all(exp.Where))
    for w in scopes:
        for pred in w.find_all(*_FILTER_OPS):
            cols = [c for c in (pred.this, pred.expression) if isinstance(c, exp.Column)]
            others = [e for e in (pred.this, pred.expression) if not isinstance(e, exp.Column)]
            # a filter = column compared to a non-column (literal / subquery / IN list)
            if not cols or not others:
                continue
            for c in cols:
                al = c.table
                real = alias2table.get(al, al)
                if "_to_" not in real or real in seen:
                    continue
                if al in selected_aliases:        # table is the subject, legit
                    continue
                if real in grounded:              # question named a value here
                    continue
                noun = _table_noun(real)
                if len(noun) >= 4 and (noun[:5] in q or noun[:-1] in q or noun in q):
                    continue                       # question mentions this table's subject
                seen.add(real)
                problems.append(
                    f"The query filters on `{real}` ({c.name}), a table the "
                    f"question never asked about. Remove that join and its "
                    f"WHERE condition -- it silently drops rows that should be "
                    f"counted. Keep only the tables needed to answer the question."
                )
    return problems


# --------------------------------------------------------------------------
# Fan-out guard
#
# The single largest source of confidently-wrong numbers here. Joining a
# one-to-many table duplicates the rows of the other side, so a SUM over it is
# silently multiplied. Measured example: "cost by donor and sector" reported
# World Bank at 28,760.93 mn against a true 19,871.73 mn (+45%), because 26
# projects carry more than one sector row. In another case the top three
# sectors summed to 108% of the entire portfolio.
#
# The check is scope-aware: aggregating in a derived table first (the correct
# pattern) puts the measure in a different SELECT scope from the fan-out join,
# so it is not flagged.
# --------------------------------------------------------------------------

AGG_FUNCS = (exp.Sum, exp.Avg)


def _alias_map(scope: exp.Expression) -> dict[str, str]:
    """alias -> real table name, for tables in this SELECT scope only."""
    out: dict[str, str] = {}
    for tbl in scope.find_all(exp.Table):
        # Skip tables belonging to a nested subquery -- different scope.
        if tbl.find_ancestor(exp.Subquery) is not None and scope.find_ancestor(
            exp.Subquery
        ) is not tbl.find_ancestor(exp.Subquery):
            continue
        name = tbl.name
        out[tbl.alias_or_name] = name
        out.setdefault(name, name)
    return out


def _grouping_aliases(select: exp.Select) -> set[str]:
    """Aliases used as a GROUP BY dimension in this scope.

    A one-to-many join is EXPECTED when the many-side is the dimension being
    grouped by: "cost by sector" should count a two-sector project in both
    sectors. It is a BUG when the fan-out table is merely along for the ride
    (e.g. joining donors just to COUNT them while summing cost). This
    distinction is what separates a legitimate breakdown from an inflated one.
    """
    out: set[str] = set()
    group = select.args.get("group")
    if group:
        for col in group.find_all(exp.Column):
            if col.table:
                out.add(col.table)
    return out


def _joined_to(select: exp.Select, alias: str) -> set[str]:
    """Aliases that `alias` is joined to via an ON condition in this scope."""
    out: set[str] = set()
    for eq in select.find_all(exp.EQ):
        cols = [c for c in (eq.this, eq.expression) if isinstance(c, exp.Column)]
        if len(cols) == 2:
            a, b = cols[0].table, cols[1].table
            if a == alias and b:
                out.add(b)
            elif b == alias and a:
                out.add(a)
    return out


def _risky_derived(select: exp.Select, grouped: set[str]) -> list[tuple[str, str]]:
    """Derived tables that still emit multiple rows per their join key."""
    out: list[tuple[str, str]] = []
    for sub in select.find_all(exp.Subquery):
        # Only subqueries used as a table in THIS scope.
        if sub.parent is not select and sub.find_ancestor(exp.Select) is not select:
            continue
        alias = sub.alias_or_name
        if not alias or alias in grouped:
            continue

        keys = {
            c.name
            for eq in select.find_all(exp.EQ)
            for c in (eq.this, eq.expression)
            if isinstance(c, exp.Column) and c.table == alias
        }
        if not keys:
            continue

        inner = sub.this if isinstance(sub.this, exp.Select) else None
        if inner is None:
            continue
        group = inner.args.get("group")
        if not group:
            continue
        gcols = {c.name for c in group.find_all(exp.Column)}
        # Grouped by the join key plus something else -> several rows per key.
        if gcols - keys:
            out.append((alias, f"{alias} (derived)"))
    return out


def check_fanout(sql: str, fanout: dict[str, list[str]]) -> list[str]:
    """Return warnings for SUM/AVG that a one-to-many join will inflate."""
    if not fanout:
        return []
    try:
        stmt = sqlglot.parse_one(sql, read="mysql")
    except Exception:
        return []

    problems: list[str] = []
    seen: set[tuple[str, str]] = set()

    for select in stmt.find_all(exp.Select):
        aliases = _alias_map(select)
        grouped = _grouping_aliases(select)

        risky: list[tuple[str, str]] = []
        for tbl in select.find_all(exp.Table):
            if tbl.find_ancestor(exp.Subquery) is not select.find_ancestor(exp.Subquery):
                continue
            if not (fanout.get(tbl.name) or []):
                continue
            al = tbl.alias_or_name
            # Justified if it IS the grouping dimension, or it is joined
            # directly to whatever is being grouped by.
            if al in grouped or (_joined_to(select, al) & grouped):
                continue
            risky.append((al, tbl.name))

        # Derived tables count too. Wrapping a junction in a subquery does NOT
        # fix the fan-out if the subquery still emits several rows per join
        # key -- e.g. `SELECT project_id, donor_id ... GROUP BY project_id,
        # donor_id` is still one row per donor. Observed in practice: the model
        # adopts this pattern when told to pre-aggregate, and the total stays
        # inflated. Flag any derived table whose GROUP BY carries columns
        # beyond the key it is joined on.
        risky += _risky_derived(select, grouped)

        if not risky:
            continue

        for agg in select.find_all(*AGG_FUNCS):
            if agg.find_ancestor(exp.Subquery) is not select.find_ancestor(exp.Subquery):
                continue
            col = agg.find(exp.Column)
            if col is None:
                continue
            owner = aliases.get(col.table or "", col.table or "")
            if not owner:
                continue
            for ralias, rname in risky:
                if rname == owner or ralias == (col.table or ""):
                    continue          # aggregating the many-side itself is fine
                key = (owner, rname)
                if key in seen:
                    continue
                seen.add(key)
                per = ", ".join(fanout.get(rname, [])) or "its join key"
                problems.append(
                    f"SUM/AVG over `{owner}`.`{col.name}` while also joining "
                    f"`{rname}`, which is not what you group by, inflates the "
                    f"total: `{rname}` has multiple rows per {per}, so each "
                    f"`{owner}` row is counted more than once. Fix it by "
                    f"collapsing to ONE row per join key -- e.g. "
                    f"(SELECT project_id, COUNT(DISTINCT donor_id) AS n "
                    f"FROM ... GROUP BY project_id) -- note the GROUP BY must "
                    f"contain ONLY the join key. Grouping by the key plus "
                    f"another column still returns several rows per key and "
                    f"does not fix anything. Or drop `{rname}` entirely."
                )

        # COUNT(*) over a fan-out join over-counts the same entity. A junction
        # with duplicate rows per project_id turns "how many projects" into a
        # row count, not a distinct-project count (Punjab: 39 vs true 36). Flag
        # a bare COUNT(*)/COUNT(col) -- but NOT COUNT(DISTINCT ...) -- whenever
        # a fan-out table is joined and more than one real table is in scope.
        real_tables_here = {
            aliases.get(t.alias_or_name, t.name)
            for t in select.find_all(exp.Table)
            if t.find_ancestor(exp.Subquery) is select.find_ancestor(exp.Subquery)
        }
        if len(real_tables_here) >= 2 and risky:
            entity = _fanout_entity_key(select, risky, fanout)
            for cnt in select.find_all(exp.Count):
                if cnt.find_ancestor(exp.Subquery) is not select.find_ancestor(exp.Subquery):
                    continue
                if cnt.find(exp.Distinct) is not None:
                    continue                       # already COUNT(DISTINCT ...)
                key = ("count", id(cnt))
                if key in seen:
                    continue
                seen.add(key)
                rnames = ", ".join(sorted({rn for _, rn in risky}))
                problems.append(
                    f"COUNT(*) over a join through {rnames} over-counts: that "
                    f"junction has duplicate rows per {entity}, so each entity "
                    f"is counted more than once. Use COUNT(DISTINCT {entity}) "
                    f"instead (the id of the entity you are counting)."
                )
                break                              # one message per scope is enough
    return problems


def _fanout_entity_key(select: exp.Select, risky, fanout) -> str:
    """The entity id to COUNT DISTINCT on -- the fan-out join column, preferring
    an *_id that appears in an ON clause (usually project_id)."""
    join_cols = {
        c.name
        for eq in select.find_all(exp.EQ)
        for c in (eq.this, eq.expression)
        if isinstance(c, exp.Column) and c.name.endswith("_id")
    }
    for _al, rname in risky:
        for col in fanout.get(rname, []):
            if col in join_cols:
                return col
    for _al, rname in risky:
        cols = fanout.get(rname, [])
        if cols:
            return cols[0]
    return "project_id"


# --------------------------------------------------------------------------
# Required predicates
#
# Some filters are not stylistic -- omitting them yields numbers that are
# wrong by orders of magnitude. Asking the model nicely is not enough (it
# dropped the amount bound on its first run), so they are enforced here and
# the omission is routed back as a repairable error.
# --------------------------------------------------------------------------

REQUIRED_PREDICATES: list[dict[str, Any]] = [  # type: ignore[name-defined]
    {
        "table": "project_to_disbursementdetails",
        "needs_any": ["sum_type"],
        "message": (
            "Aggregating project_to_disbursementdetails without filtering "
            "sum_type double-counts: sum_type='1' rows are subtotals of the "
            "sum_type='0' detail rows. Add AND d.sum_type = '0'."
        ),
        "only_if_aggregating": True,
    },
    {
        "table": "project_to_disbursementdetails",
        "needs_any": ["100000", "< 100000", "<100000"],
        "message": (
            "Aggregating amount_usd without a plausibility bound includes 6 "
            "rows that were entered in raw dollars instead of millions (e.g. "
            "122800000 where 122.8 was meant); they inflate the total ~1e6x. "
            "Add AND CAST(<alias>.amount_usd AS DECIMAL(20,2)) < 100000."
        ),
        "only_if_aggregating": True,
        "only_if_column": "amount_usd",
    },
]


def check_required_predicates(sql: str) -> list[str]:
    low = " ".join(sql.lower().split())
    problems = []
    aggregating = any(fn in low for fn in ("sum(", "avg(", "count(", "group by"))

    for rule in REQUIRED_PREDICATES:
        if rule["table"] not in low:
            continue
        if rule.get("only_if_aggregating") and not aggregating:
            continue
        col = rule.get("only_if_column")
        if col and col not in low:
            continue
        if not any(tok.lower() in low for tok in rule["needs_any"]):
            problems.append(rule["message"])
    return problems
