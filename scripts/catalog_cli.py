"""Rebuild / inspect the schema catalog.

    python catalog_cli.py --rebuild        rebuild from the live DB
    python catalog_cli.py --stats          summary
    python catalog_cli.py --joins TABLE    show inferred joins for a table
    python catalog_cli.py --path A B       show how two tables connect
"""
import argparse
import sys
from pathlib import Path

# Runs from scripts/ -- make the project root importable.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ead_agent.schema_catalog import (  # noqa: E402
    _shortest_path,
    build_catalog,
    join_hints,
    load_catalog,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--joins", metavar="TABLE")
    ap.add_argument("--path", nargs=2, metavar=("A", "B"))
    args = ap.parse_args()

    catalog = build_catalog(force=True) if args.rebuild else load_catalog()
    if args.rebuild:
        print(f"rebuilt: {len(catalog['tables'])} tables -> schema_catalog.json")

    graph = catalog["join_graph"]

    if args.stats or args.rebuild:
        tables = catalog["tables"]
        junction = sum(1 for t in tables.values() if t["is_junction"])
        framework = sum(1 for t in tables.values() if t["is_framework"])
        commented = sum(
            1 for t in tables.values() for c in t["columns"] if c["comment"]
        )
        print(f"  tables          : {len(tables)}")
        print(f"  junction (_to_) : {junction}")
        print(f"  framework       : {framework}")
        print(f"  columns w/ notes: {commented}")
        print(f"  pk index        : {len(graph['pk_index'])}")
        print(f"  inferred joins  : {len(graph['edges'])}")
        isolated = [n for n in tables if n not in graph["adjacency"]]
        print(f"  isolated tables : {len(isolated)}")

    if args.joins:
        t = args.joins
        nbrs = graph["adjacency"].get(t, {})
        print(f"\n{t} -> {len(nbrs)} neighbours")
        for other, pairs in sorted(nbrs.items()):
            for ca, cb in pairs:
                print(f"    {t}.{ca}  =  {other}.{cb}")

    if args.path:
        a, b = args.path
        p = _shortest_path(a, b, graph["adjacency"], max_hops=3)
        print(f"\npath {a} -> {b}: {' -> '.join(p) if p else 'NO PATH within 3 hops'}")
        if p:
            for h in join_hints(p, graph):
                print("   ", h)


if __name__ == "__main__":
    main()
