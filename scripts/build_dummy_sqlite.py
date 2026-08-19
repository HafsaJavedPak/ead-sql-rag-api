"""Build a local SQLite analytics database from the INSERT-only dummy dump."""

from __future__ import annotations

import argparse
import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import sqlglot
from sqlglot import exp

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "ead_dummy_data_atomcamp.sql"
DEFAULT_DATABASE = ROOT / ".local" / "ead_dummy.db"
DEFAULT_SCHEMA = ROOT / "ead_dummy_schema.sqlite.sql"
DEFAULT_MYSQL_SCHEMA = ROOT / "ead_dummy_schema.mysql.sql"


@dataclass(frozen=True)
class TableData:
    name: str
    columns: list[str]
    rows: list[list[Any]]
    types: list[str]
    primary_key: str | None


def _literal(value: exp.Expression) -> Any:
    if isinstance(value, exp.Null):
        return None
    if not isinstance(value, exp.Literal):
        raise ValueError(f"Unsupported value node: {type(value).__name__}")
    if value.is_string:
        return value.this
    raw = value.this
    try:
        return int(raw)
    except ValueError:
        return float(raw)


def _column_type(values: list[Any]) -> str:
    present = [value for value in values if value is not None]
    if any(isinstance(value, str) for value in present):
        return "TEXT"
    if any(isinstance(value, float) for value in present):
        return "REAL"
    return "INTEGER"


def _primary_key(columns: list[str], rows: list[list[Any]]) -> str | None:
    if not columns or not rows:
        return None
    candidate = columns[0]
    if candidate != "id" and not candidate.endswith("_id"):
        return None
    values = [row[0] for row in rows]
    if any(value is None for value in values) or len(set(values)) != len(values):
        return None
    return candidate


def parse_dump(source: Path) -> list[TableData]:
    statements = sqlglot.parse(source.read_text(encoding="utf-8"), read="mysql")
    parsed: dict[str, tuple[list[str], list[list[Any]]]] = {}
    for statement in statements:
        if not isinstance(statement, exp.Insert):
            continue
        if not isinstance(statement.this, exp.Schema) or not isinstance(
            statement.expression, exp.Values
        ):
            raise ValueError("Expected INSERT with explicit columns and VALUES")
        table = statement.this.this
        if not isinstance(table, exp.Table):
            raise ValueError("Expected a named INSERT target")
        columns = [column.name for column in statement.this.expressions]
        rows = [
            [_literal(value) for value in row.expressions]
            for row in statement.expression.expressions
        ]
        if any(len(row) != len(columns) for row in rows):
            raise ValueError(f"Column/value mismatch in {table.name}")
        if table.name in parsed:
            existing_columns, existing_rows = parsed[table.name]
            if existing_columns != columns:
                raise ValueError(f"Conflicting column lists for {table.name}")
            existing_rows.extend(rows)
        else:
            parsed[table.name] = (columns, rows)

    tables: list[TableData] = []
    for table_name, (columns, rows) in parsed.items():
        types = [_column_type([row[index] for row in rows]) for index in range(len(columns))]
        tables.append(
            TableData(
                name=table_name,
                columns=columns,
                rows=rows,
                types=types,
                primary_key=_primary_key(columns, rows),
            )
        )
    if not parsed:
        raise ValueError("No INSERT statements found")
    return tables


def _quote(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def schema_sql(tables: list[TableData]) -> str:
    statements = [
        "-- Generated from ead_dummy_data_atomcamp.sql.\n",
        "-- SQLite schema for local SQL-RAG testing; production remains MySQL.\n",
        "PRAGMA foreign_keys = OFF;\n\n",
    ]
    for table in tables:
        definitions = []
        for column, data_type in zip(table.columns, table.types, strict=True):
            suffix = " PRIMARY KEY" if column == table.primary_key else ""
            definitions.append(f"  {_quote(column)} {data_type}{suffix}")
        statements.append(f"CREATE TABLE {_quote(table.name)} (\n")
        statements.append(",\n".join(definitions))
        statements.append("\n);\n")
        for column in table.columns:
            if column.endswith("_id") and column != table.primary_key:
                index_name = f"ix_{table.name}_{column}"
                statements.append(
                    f"CREATE INDEX {_quote(index_name)} ON "
                    f"{_quote(table.name)} ({_quote(column)});\n"
                )
        statements.append("\n")
    return "".join(statements)


def _mysql_quote(identifier: str) -> str:
    return "`" + identifier.replace("`", "``") + "`"


def _mysql_type(column: str, data_type: str, values: list[Any]) -> str:
    if data_type == "INTEGER":
        return "BIGINT"
    if data_type == "REAL":
        return "DOUBLE"
    maximum = max((len(value) for value in values if isinstance(value, str)), default=0)
    if column.endswith("_id") or maximum <= 255:
        return "VARCHAR(255)"
    return "LONGTEXT"


def mysql_schema_sql(tables: list[TableData]) -> str:
    statements = [
        "-- Generated from ead_dummy_data_atomcamp.sql.\n",
        "-- MySQL schema for the synthetic SQL-RAG test dataset.\n",
        "SET NAMES utf8mb4;\n",
        "SET FOREIGN_KEY_CHECKS = 0;\n\n",
    ]
    for table in tables:
        definitions = []
        for index, (column, data_type) in enumerate(
            zip(table.columns, table.types, strict=True)
        ):
            values = [row[index] for row in table.rows]
            mysql_type = _mysql_type(column, data_type, values)
            suffix = " NOT NULL PRIMARY KEY" if column == table.primary_key else " NULL"
            definitions.append(f"  {_mysql_quote(column)} {mysql_type}{suffix}")
        for column in table.columns:
            if column.endswith("_id") and column != table.primary_key:
                definitions.append(
                    f"  KEY {_mysql_quote(f'ix_{table.name}_{column}')} "
                    f"({_mysql_quote(column)})"
                )
        statements.append(f"CREATE TABLE {_mysql_quote(table.name)} (\n")
        statements.append(",\n".join(definitions))
        statements.append(
            "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 "
            "COLLATE=utf8mb4_unicode_ci;\n\n"
        )
    statements.append("SET FOREIGN_KEY_CHECKS = 1;\n")
    return "".join(statements)


def build_database(tables: list[TableData], database: Path, schema: str) -> int:
    database.parent.mkdir(parents=True, exist_ok=True)
    if database.exists():
        database.unlink()
    row_count = 0
    with sqlite3.connect(database) as connection:
        connection.executescript(schema)
        for table in tables:
            placeholders = ",".join("?" for _ in table.columns)
            columns = ",".join(_quote(column) for column in table.columns)
            connection.executemany(
                f"INSERT INTO {_quote(table.name)} ({columns}) VALUES ({placeholders})",
                table.rows,
            )
            row_count += len(table.rows)
        connection.commit()
        connection.execute("PRAGMA optimize")
    return row_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--schema-out", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--mysql-schema-out", type=Path, default=DEFAULT_MYSQL_SCHEMA)
    args = parser.parse_args()

    tables = parse_dump(args.source)
    schema = schema_sql(tables)
    args.schema_out.write_text(schema, encoding="utf-8")
    mysql_schema = mysql_schema_sql(tables)
    args.mysql_schema_out.write_text(mysql_schema, encoding="utf-8")
    rows = build_database(tables, args.database, schema)
    digest = hashlib.sha256(args.source.read_bytes()).hexdigest()[:16]
    print(
        f"Built {args.database} with {len(tables)} tables and {rows} rows (source sha256 {digest})."
    )
    print(f"Wrote executable SQLite schema to {args.schema_out}.")
    print(f"Wrote executable MySQL schema to {args.mysql_schema_out}.")


if __name__ == "__main__":
    main()
