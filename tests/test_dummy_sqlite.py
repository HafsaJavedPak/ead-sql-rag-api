from __future__ import annotations

import sqlite3
from pathlib import Path

from scripts.build_dummy_sqlite import build_database, parse_dump, schema_sql

ROOT = Path(__file__).resolve().parents[1]


def test_insert_only_dump_builds_complete_sqlite_database(tmp_path: Path) -> None:
    tables = parse_dump(ROOT / "ead_dummy_data_atomcamp.sql")

    assert len(tables) == 145
    assert sum(len(table.rows) for table in tables) == 4930
    assert len({table.name for table in tables}) == len(tables)

    database = tmp_path / "dummy.db"
    rows = build_database(tables, database, schema_sql(tables))
    assert rows == 4930

    with sqlite3.connect(database) as connection:
        table_count = connection.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table'"
        ).fetchone()[0]
        project_count = connection.execute("SELECT COUNT(*) FROM wq_projects").fetchone()[0]
        connection.execute("PRAGMA query_only = ON")
        assert table_count == 145
        assert project_count == 120
        try:
            connection.execute("CREATE TABLE forbidden (id INTEGER)")
        except sqlite3.OperationalError:
            pass
        else:
            raise AssertionError("SQLite query_only mode allowed a write")
