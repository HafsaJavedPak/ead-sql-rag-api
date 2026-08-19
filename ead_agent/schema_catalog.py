"""Live schema introspection -> cached catalog + inferred join graph.

Two jobs:

1.  CATALOG. Read INFORMATION_SCHEMA for all 146 tables: columns, types,
    column comments (which carry the status-code legends), primary keys and
    row counts. Cache to schema_catalog.json.

2.  JOIN GRAPH. This schema has exactly ONE declared FOREIGN KEY, so joins
    cannot be read from constraints -- they have to be inferred. The rule
    that actually holds here: a column named `<x>_id` refers to the table
    whose PRIMARY KEY is also `<x>_id`. We build a PK index, then match
    every `*_id` column against it. Self-referencing columns (a table's own
    PK) are skipped.

    Inference is deterministic and inspectable on purpose -- the LLM picks
    *which* tables are relevant, but never invents how they join.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from typing import Any

from sqlalchemy import inspect, text

from ead_agent.config import settings
from ead_agent.db import admin_engine

# Tables that are Laravel framework plumbing, not EAD domain data. They are
# still catalogued (a question could legitimately be about jobs/users) but are
# down-weighted so they don't crowd out real tables in retrieval.
FRAMEWORK_TABLES = {
    "cache",
    "cache_locks",
    "failed_jobs",
    "jobs",
    "job_batches",
    "migrations",
    "notifications",
    "password_reset_tokens",
    "personal_access_tokens",
    "sessions",
}


@dataclass
class Column:
    name: str
    data_type: str  # e.g. "varchar(255)", "decimal(20,2)"
    nullable: bool
    comment: str = ""
    is_pk: bool = False


@dataclass
class Table:
    name: str
    columns: list[Column] = field(default_factory=list)
    primary_key: list[str] = field(default_factory=list)
    row_count: int = 0
    description: str = ""
    is_junction: bool = False
    is_framework: bool = False

    def column_names(self) -> list[str]:
        return [c.name for c in self.columns]

    def ddl(self) -> str:
        """Compact CREATE-TABLE-ish text for the generate_sql prompt.

        Not valid DDL to execute -- it is a token-efficient description. Column
        comments are inlined because they carry the status-code legends the
        model needs (e.g. '1=ongoing, 2=completed').
        """
        lines = [f"CREATE TABLE `{self.name}` ("]
        for c in self.columns:
            bits = [f"  `{c.name}` {c.data_type}"]
            if c.is_pk:
                bits.append("PRIMARY KEY")
            if not c.nullable:
                bits.append("NOT NULL")
            line = " ".join(bits)
            if c.comment:
                line += f"  -- {c.comment}"
            lines.append(line + ",")
        lines.append(f")  -- {self.description} ({self.row_count:,} rows)")
        return "\n".join(lines)

    def doc(self) -> str:
        """Short text used for embedding/retrieval. Must stay small: 146 of
        these are embedded, and the refine prompt lists many at once."""
        cols = ", ".join(self.column_names()[:24])
        return f"{self.name}: {self.description}. Columns: {cols}"


def _humanize(table_name: str) -> str:
    """wq_piplineprojects -> 'pipline projects';  project_to_donors -> 'project to donors'."""
    n = re.sub(r"^wq_", "", table_name)
    n = n.replace("_", " ")
    return n.strip()


def _describe(name: str, columns: list[Column], row_count: int) -> str:
    """One-line description inferred from name + columns. Deterministic --
    no LLM call, because this runs over every table on every rebuild."""
    human = _humanize(name)
    if name in FRAMEWORK_TABLES:
        return f"Laravel framework table ({human}); not EAD domain data"

    junction_prefix = ""
    if "_to_" in name:
        left, right = name.split("_to_", 1)
        junction_prefix = (
            f"Junction table linking {_humanize(left)} to {right.replace('_', ' ')}"
            f"; holds the many-to-many relationship and any per-link attributes"
        )
        # Do NOT return early. Junction tables carry the measures -- e.g.
        # project_to_financials holds project_cost / projectcost_usd / loan /
        # grant. Without the column hints below it was described only as a
        # link table and lost retrieval to wq_piplineprojects on cost
        # questions, which has 3 rows.

    hints = []
    cn = {c.name for c in columns}
    if any(c.endswith("_usd") for c in cn):
        hints.append("has USD amounts")
    if any(c.endswith("_pkr") for c in cn):
        hints.append("has PKR amounts")
    if "exchange_rate" in cn or any("exchange" in c for c in cn):
        hints.append("has exchange rates")
    # NOTE: timeperiod_id is deliberately NOT treated as a fiscal-year marker.
    # wq_timeperiods holds disbursement *frequencies* (Quarterly, Annually,
    # 'Since date of signing'), not fiscal years. Verified against live data.
    if any(c in cn for c in ("fiscal_year", "fiscalyear")):
        hints.append("has a fiscal_year column (check its format -- some are date-range strings)")
    if "from" in cn and "to" in cn:
        hints.append("date-bounded rows: derive fiscal year from `from`/`to`")
    if "timeperiod_id" in cn:
        hints.append("timeperiod_id = disbursement FREQUENCY, not fiscal year")
    if any(c.startswith("month") for c in cn):
        hints.append("monthly breakdown")
    if any(c.endswith("_status") for c in cn):
        hints.append("has a status code")
    if "sum_type" in cn:
        hints.append("sum_type: 1=subtotal row, 0=detail entry -- filter to '0' when aggregating")

    # Surface the money/measure columns by name -- retrieval matches on these.
    measures = [
        c
        for c in sorted(cn)
        if any(k in c for k in ("cost", "amount", "loan", "grant", "disburse", "value"))
    ][:6]
    if measures:
        hints.append("measures: " + ", ".join(measures))

    base = junction_prefix or f"EAD master/reference data for {human}"
    if hints:
        base += " (" + "; ".join(hints) + ")"
    return base


def introspect() -> dict[str, Table]:
    """Read the live database. Requires the admin (non-readonly) user."""
    eng = admin_engine()
    if eng.dialect.name == "sqlite":
        return _introspect_sqlite(eng)
    db = settings.db_name
    tables: dict[str, Table] = {}

    with eng.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT table_name, COALESCE(table_rows, 0)
                FROM information_schema.tables
                WHERE table_schema = :db AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """
            ),
            {"db": db},
        ).fetchall()
        for tname, rcount in rows:
            tables[tname] = Table(
                name=tname,
                row_count=int(rcount or 0),
                is_junction="_to_" in tname,
                is_framework=tname in FRAMEWORK_TABLES,
            )

        cols = conn.execute(
            text(
                """
                SELECT table_name, column_name, column_type, is_nullable,
                       column_comment, column_key
                FROM information_schema.columns
                WHERE table_schema = :db
                ORDER BY table_name, ordinal_position
                """
            ),
            {"db": db},
        ).fetchall()

    for tname, cname, ctype, nullable, comment, ckey in cols:
        if tname not in tables:
            continue
        is_pk = ckey == "PRI"
        tables[tname].columns.append(
            Column(
                name=cname,
                data_type=ctype,
                nullable=(nullable == "YES"),
                comment=(comment or "").strip(),
                is_pk=is_pk,
            )
        )
        if is_pk:
            tables[tname].primary_key.append(cname)

    for t in tables.values():
        t.description = _describe(t.name, t.columns, t.row_count)

    return tables


def _introspect_sqlite(eng) -> dict[str, Table]:
    """Build the catalog from the generated local SQLite dummy database."""
    inspector = inspect(eng)
    tables: dict[str, Table] = {}
    with eng.connect() as connection:
        for table_name in sorted(inspector.get_table_names()):
            quoted = table_name.replace('"', '""')
            row_count = int(
                connection.execute(text(f'SELECT COUNT(*) FROM "{quoted}"')).scalar() or 0
            )
            primary_key = set(
                inspector.get_pk_constraint(table_name).get("constrained_columns") or []
            )
            columns = [
                Column(
                    name=str(column["name"]),
                    data_type=str(column["type"]).lower(),
                    nullable=bool(column.get("nullable", True)),
                    is_pk=str(column["name"]) in primary_key,
                )
                for column in inspector.get_columns(table_name)
            ]
            table = Table(
                name=table_name,
                columns=columns,
                primary_key=[column.name for column in columns if column.is_pk],
                row_count=row_count,
                is_junction="_to_" in table_name,
                is_framework=table_name in FRAMEWORK_TABLES,
            )
            table.description = _describe(table.name, table.columns, table.row_count)
            tables[table_name] = table
    return tables


# --------------------------------------------------------------------------
# Join graph -- the part that replaces the missing foreign keys
# --------------------------------------------------------------------------


def build_join_graph(tables: dict[str, Table]) -> dict[str, Any]:
    """Infer joins from the `<x>_id` naming convention.

    Returns:
        pk_index: {pk_column_name: table_name}  for single-column integer PKs
        edges:    [{from_table, from_column, to_table, to_column}, ...]
        adjacency: {table: {neighbour_table: [(col_here, col_there), ...]}}
    """
    # A PK only anchors joins if it is a single column and looks like an id.
    pk_index: dict[str, str] = {}
    for t in tables.values():
        if len(t.primary_key) == 1 and t.primary_key[0].endswith("_id"):
            pk_index.setdefault(t.primary_key[0], t.name)

    edges: list[dict[str, str]] = []
    unresolved: list[tuple[str, str]] = []
    for t in tables.values():
        own_pk = set(t.primary_key)
        for c in t.columns:
            if not c.name.endswith("_id") or c.name in own_pk:
                continue
            target = pk_index.get(c.name)
            if target and target != t.name:
                edges.append(
                    {
                        "from_table": t.name,
                        "from_column": c.name,
                        "to_table": target,
                        "to_column": c.name,
                    }
                )
            elif not target:
                unresolved.append((t.name, c.name))

    # Second pass: suffix aliases.
    #
    # Some columns reference a table without matching its PK name exactly --
    # course_to_sectors.sector_id really does point at
    # wq_projectsectors.projectsector_id (verified: 176/176 rows match).
    # Match on PK-name suffix, then CONFIRM against real data before
    # accepting the edge, so we never invent a join from a name coincidence.
    edges.extend(_alias_edges(unresolved, pk_index, tables))

    adjacency: dict[str, dict[str, list[tuple[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for e in edges:
        adjacency[e["from_table"]][e["to_table"]].append((e["from_column"], e["to_column"]))
        adjacency[e["to_table"]][e["from_table"]].append((e["to_column"], e["from_column"]))

    return {
        "pk_index": pk_index,
        "edges": edges,
        "adjacency": {k: {k2: v2 for k2, v2 in v.items()} for k, v in adjacency.items()},
        "fanout": _measure_fanout(edges, tables),
    }


def _measure_fanout(edges: list[dict[str, str]], tables: dict[str, Table]) -> dict[str, list[str]]:
    """For every join column, is it unique in its own table?

    A non-unique join column means joining that table MULTIPLIES rows -- and a
    SUM on the other side is then silently inflated. Measured, not assumed:
    26 of 289 projects carry more than one sector row, which is why
    "cost by donor and sector" over-reported World Bank by 45%.

    Returns {table: [columns that are NOT unique]}.
    """
    from sqlalchemy import text

    pairs: set[tuple[str, str]] = set()
    for e in edges:
        pairs.add((e["from_table"], e["from_column"]))
        pairs.add((e["to_table"], e["to_column"]))

    out: dict[str, list[str]] = defaultdict(list)
    try:
        with admin_engine().connect() as conn:
            for tname, col in sorted(pairs):
                if tables.get(tname) is None or tables[tname].row_count == 0:
                    continue
                try:
                    row = conn.execute(
                        text(
                            f"SELECT COUNT(*) AS n, COUNT(DISTINCT `{col}`) AS d "
                            f"FROM `{tname}` WHERE `{col}` IS NOT NULL"
                        )
                    ).fetchone()
                except Exception:
                    continue
                n, d = int(row[0] or 0), int(row[1] or 0)
                if n and d and n > d:
                    out[tname].append(col)
    except Exception:
        return {}
    return dict(out)


# A candidate alias is only accepted if at least this share of non-null values
# actually resolves to a row in the target table. Guards against name
# coincidences (e.g. `user_id` in two unrelated subsystems).
ALIAS_MIN_MATCH = 0.95


def _alias_edges(
    unresolved: list[tuple[str, str]],
    pk_index: dict[str, str],
    tables: dict[str, Table],
) -> list[dict[str, str]]:
    """Resolve `<stem>_id` columns against PKs named `<prefix><stem>_id`.

    Every candidate is checked against the live data; a link is kept only if
    virtually all values resolve. Requires DB access -- if that fails we
    simply return nothing rather than guessing.
    """
    from sqlalchemy import text

    candidates: list[tuple[str, str, str, str]] = []
    for tname, cname in unresolved:
        stem = cname[:-3]  # sector_id -> sector
        if len(stem) < 4:  # too short to be distinctive
            continue
        for pk_name, target in pk_index.items():
            if target == tname or pk_name == cname:
                continue
            if pk_name.endswith(cname) or pk_name[:-3].endswith(stem):
                candidates.append((tname, cname, target, pk_name))

    if not candidates:
        return []

    accepted: list[dict[str, str]] = []
    try:
        eng = admin_engine()
        with eng.connect() as conn:
            for tname, cname, target, pk_name in candidates:
                if tables[tname].row_count == 0:
                    continue
                try:
                    row = conn.execute(
                        text(
                            f"SELECT COUNT(*) AS n, "
                            f"SUM(b.`{pk_name}` IS NOT NULL) AS matched "
                            f"FROM `{tname}` a "
                            f"LEFT JOIN `{target}` b ON a.`{cname}` = b.`{pk_name}` "
                            f"WHERE a.`{cname}` IS NOT NULL"
                        )
                    ).fetchone()
                except Exception:
                    continue
                n, matched = (row[0] or 0), int(row[1] or 0)
                if n and matched / n >= ALIAS_MIN_MATCH:
                    accepted.append(
                        {
                            "from_table": tname,
                            "from_column": cname,
                            "to_table": target,
                            "to_column": pk_name,
                        }
                    )
    except Exception:
        return []
    return accepted


def connect_tables(
    selected: list[str],
    adjacency: dict[str, dict[str, list]],
    max_hops: int = 2,
    preferred: set[str] | None = None,
) -> list[str]:
    """Add the bridging tables needed to make `selected` actually joinable.

    The LLM routinely picks two tables that are only connected through a
    junction table it forgot to mention (wq_donors + wq_projects need
    project_to_foreigncecomponents, for example).

    `preferred` should be the retriever's candidate set. It matters: the
    structurally shortest path is often semantically wrong. wq_donors reaches
    wq_regions in 4 hops via course_to_donors -> wq_courses ->
    course_to_applicants, i.e. through the *training courses* subsystem, which
    is nonsense for a question about project funding by region. Routing
    through tables the retriever already judged relevant to the question keeps
    bridges inside the right domain.
    """
    if len(selected) < 2:
        return list(dict.fromkeys(selected))

    needed: set[str] = set(selected)
    for i, src in enumerate(selected):
        for dst in selected[i + 1 :]:
            path = _shortest_path(src, dst, adjacency, max_hops, preferred)
            if path:
                needed.update(path)

    # Preserve the model's ordering first, then appended bridges.
    ordered = list(dict.fromkeys(selected))
    ordered += sorted(needed - set(ordered))
    return ordered


# Cost of routing through a table the retriever did NOT surface. High enough
# that any in-domain route wins, low enough that a genuine bridge still beats
# no path at all.
OFF_DOMAIN_COST = 10


def _shortest_path(
    src: str,
    dst: str,
    adjacency: dict[str, dict[str, list]],
    max_hops: int,
    preferred: set[str] | None = None,
) -> list[str] | None:
    """Uniform-cost search. With `preferred` supplied this is no longer plain
    BFS: intermediate tables outside the candidate set cost OFF_DOMAIN_COST,
    so a 2-hop in-domain route beats a 1-hop detour through an unrelated
    subsystem. `max_hops` still caps path *length* regardless of cost.
    """
    if src == dst:
        return [src]

    import heapq

    best: dict[str, int] = {src: 0}
    heap: list[tuple[int, int, str, list[str]]] = [(0, 0, src, [src])]
    counter = 0

    while heap:
        cost, _, node, path = heapq.heappop(heap)
        if len(path) - 1 >= max_hops:
            continue
        for nxt in adjacency.get(node, {}):
            if nxt in path:
                continue
            step = 1 if (preferred is None or nxt in preferred or nxt == dst) else OFF_DOMAIN_COST
            new_cost = cost + step
            if nxt == dst:
                return path + [nxt]
            if new_cost < best.get(nxt, 1 << 30):
                best[nxt] = new_cost
                counter += 1
                heapq.heappush(heap, (new_cost, counter, nxt, path + [nxt]))
    return None


def join_hints(tables: list[str], graph: dict[str, Any]) -> list[str]:
    """Human/LLM-readable ON clauses for the selected tables, so generate_sql
    never has to guess a join condition."""
    adjacency = graph["adjacency"]
    hints, seen = [], set()
    for a in tables:
        for b, pairs in adjacency.get(a, {}).items():
            if b not in tables:
                continue
            key = tuple(sorted([a, b]))
            if key in seen:
                continue
            seen.add(key)
            for ca, cb in pairs:
                hints.append(f"`{a}`.`{ca}` = `{b}`.`{cb}`")
    return hints


# --------------------------------------------------------------------------
# Value index -- which lookup table actually contains a given name?
#
# Retrieval matches table DESCRIPTIONS, so a question naming a value has
# nothing to match on. "Active projects in Punjab" produced SQL joining
# wq_projectsectors, because nothing told the model that "Punjab" is a REGION
# and not a sector. Indexing the values of small lookup tables lets us say so
# outright, deterministically, before any SQL is written.
# --------------------------------------------------------------------------

VALUE_INDEX_MAX_ROWS = 3000  # only index small lookup/reference tables
VALUE_INDEX_MAX_PER_TABLE = 400
VALUE_MIN_LEN = 3


def build_value_index(tables: dict[str, Table]) -> dict[str, list[str]]:
    """{lowercased value: ["table.column", ...]} for small reference tables."""
    from sqlalchemy import text

    index: dict[str, list[str]] = defaultdict(list)
    try:
        with admin_engine().connect() as conn:
            for t in tables.values():
                if t.row_count == 0 or t.row_count > VALUE_INDEX_MAX_ROWS:
                    continue
                if t.is_framework:
                    continue
                for c in t.columns:
                    # Human-readable label columns only.
                    if not (c.name.endswith("_name") or c.name.endswith("_short")):
                        continue
                    if not c.data_type.startswith(("varchar", "char", "text")):
                        continue
                    try:
                        rows = conn.execute(
                            text(
                                f"SELECT DISTINCT `{c.name}` FROM `{t.name}` "
                                f"WHERE `{c.name}` IS NOT NULL AND `{c.name}` <> '' "
                                f"LIMIT {VALUE_INDEX_MAX_PER_TABLE}"
                            )
                        ).fetchall()
                    except Exception:
                        continue
                    for (val,) in rows:
                        v = str(val).strip().lower()
                        if len(v) < VALUE_MIN_LEN:
                            continue
                        ref = f"{t.name}.{c.name}"
                        if ref not in index[v]:
                            index[v].append(ref)
    except Exception:
        return {}
    return dict(index)


# Generic words that happen to be stored as status/lookup labels. Reporting
# them as "values" sends the model chasing a status table -- notably
# wq_projectstatuses, which is the documented trap for decoding
# wq_projects.project_status. Treat them as ordinary English.
VALUE_STOPWORDS = {
    "active",
    "inactive",
    "completed",
    "closed",
    "ongoing",
    "pending",
    "approved",
    "rejected",
    "other",
    "test",
    "none",
    "total",
    "sample",
    "new",
    "old",
    "all",
    "yes",
    "no",
}


def _rank_ref(ref: str) -> tuple[int, int]:
    """Sort key for candidate columns: canonical master tables win."""
    table, column = ref.split(".", 1)
    score = 0
    if table.startswith("wq_"):
        score -= 2  # master/reference table
    if "_to_" in table:
        score += 2  # junction: rarely the canonical home
    if column.endswith("_name"):
        score -= 1
    if column.endswith("_short"):
        score += 1
    return (score, len(table))


def match_values(question: str, value_index: dict[str, list[str]]) -> list[tuple[str, str]]:
    """Return [(matched_value, "table.column"), ...] for values named in the
    question. Longest matches first so "Khyber Pakhtunkhwa" wins over "Khyber"."""
    q = " " + question.lower() + " "
    hits: list[tuple[str, str]] = []
    seen: set[str] = set()
    for val in sorted(value_index, key=len, reverse=True):
        if len(val) < 4 or val in VALUE_STOPWORDS:
            continue
        if val in q and val not in seen:
            # crude word-boundary check to avoid matching inside longer words
            i = q.find(val)
            before, after = q[i - 1], q[i + len(val)] if i + len(val) < len(q) else " "
            if not before.isalnum() and not after.isalnum():
                seen.add(val)
                for ref in sorted(value_index[val], key=_rank_ref)[:1]:
                    hits.append((val, ref))
        if len(hits) >= 5:
            break
    return hits


# --------------------------------------------------------------------------
# Cache
# --------------------------------------------------------------------------


def build_catalog(force: bool = False) -> dict[str, Any]:
    if settings.catalog_path.exists() and not force:
        return json.loads(settings.catalog_path.read_text(encoding="utf-8"))

    tables = introspect()
    graph = build_join_graph(tables)
    catalog = {
        "database": settings.db_name,
        "tables": {name: asdict(t) for name, t in tables.items()},
        "join_graph": graph,
        "value_index": build_value_index(tables),
    }
    settings.catalog_path.parent.mkdir(parents=True, exist_ok=True)
    settings.catalog_path.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return catalog


def load_catalog() -> dict[str, Any]:
    if not settings.catalog_path.exists():
        return build_catalog(force=True)
    return json.loads(settings.catalog_path.read_text(encoding="utf-8"))


def table_objects(catalog: dict[str, Any]) -> dict[str, Table]:
    out = {}
    for name, d in catalog["tables"].items():
        cols = [Column(**c) for c in d["columns"]]
        out[name] = Table(
            name=d["name"],
            columns=cols,
            primary_key=d["primary_key"],
            row_count=d["row_count"],
            description=d["description"],
            is_junction=d["is_junction"],
            is_framework=d["is_framework"],
        )
    return out
