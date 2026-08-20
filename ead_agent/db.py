"""Two engines, deliberately separated.

    admin_engine()    -- INFORMATION_SCHEMA introspection only.
    readonly_engine() -- the ONLY engine that ever runs model-generated SQL.
                         Backed by a GRANT SELECT-only user (see setup.md).

Belt and suspenders: even if validate_sql were bypassed, the read-only grant
means a write statement fails at the server.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Engine

from ead_agent.config import CACHE_DIR, settings

_admin: Engine | None = None
_readonly: Engine | None = None


def _url(user: str, password: str) -> str:
    from urllib.parse import quote_plus

    return (
        f"mysql+pymysql://{quote_plus(user)}:{quote_plus(password)}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}?charset=utf8mb4"
    )


def _analytics_url(user: str, password: str) -> str:
    return settings.analytics_database_url or _url(user, password)


_ssl_ca_path: Path | None = None


def _ssl_connect_args() -> dict[str, Any]:
    """PyMySQL SSL args for managed hosts that enforce TLS (e.g. Aiven).

    SQLAlchemy's mysql+pymysql:// URL has no query-string way to pass a CA
    certificate -- PyMySQL wants it as a connect_args dict instead. Settings
    carries the certificate as PEM content (an env var), not a path, since
    that's the one thing every one of this app's deploy targets can pass
    through; write it to a local file once and hand PyMySQL that path.
    """
    if not settings.db_ssl_ca:
        return {}
    global _ssl_ca_path
    if _ssl_ca_path is None:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path = CACHE_DIR / "db_ssl_ca.pem"
        path.write_text(settings.db_ssl_ca)
        _ssl_ca_path = path
    return {"ssl": {"ca": str(_ssl_ca_path)}}


def _engine(user: str, password: str, *, readonly: bool) -> Engine:
    url = _analytics_url(user, password)
    if url.startswith("sqlite:"):
        engine = create_engine(url)
        if readonly:

            @event.listens_for(engine, "connect")
            def enable_query_only(dbapi_connection, _connection_record) -> None:
                dbapi_connection.execute("PRAGMA query_only = ON")

        return engine
    connect_args: dict[str, Any] = {"connect_timeout": 10, **_ssl_connect_args()}
    if readonly:
        connect_args["read_timeout"] = settings.query_timeout_seconds + 5
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)


def admin_engine() -> Engine:
    global _admin
    if _admin is None:
        _admin = _engine(settings.db_user, settings.db_password, readonly=False)
    return _admin


def readonly_engine() -> Engine:
    global _readonly
    if _readonly is None:
        _readonly = _engine(
            settings.db_readonly_user,
            settings.db_readonly_password,
            readonly=True,
        )
    return _readonly


def run_readonly(sql: str) -> tuple[list[str], list[tuple[Any, ...]]]:
    """Execute one SELECT as the read-only user. Returns (columns, rows).

    Enforces a server-side statement timeout so a runaway join can't pin the
    database. Raises on any DB error -- the caller (execute_sql node) turns
    that into the self-repair signal.
    """
    ms = settings.query_timeout_seconds * 1000
    with readonly_engine().connect() as conn:
        if conn.dialect.name == "mysql":
            # These safeguards are MySQL session controls; SQLite uses query_only.
            conn.execute(text(f"SET SESSION MAX_EXECUTION_TIME={ms}"))
            conn.execute(text("SET SESSION sql_mode='ONLY_FULL_GROUP_BY'"))
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = [tuple(r) for r in result.fetchall()]
    return columns, rows


def ping() -> dict[str, Any]:
    """Connectivity check used by setup verification and app startup."""
    out: dict[str, Any] = {}
    with admin_engine().connect() as conn:
        if conn.dialect.name == "sqlite":
            out["version"] = conn.execute(text("SELECT sqlite_version()")).scalar()
            out["tables"] = len(inspect(conn).get_table_names())
        else:
            out["version"] = conn.execute(text("SELECT VERSION()")).scalar()
            out["tables"] = conn.execute(
                text(
                    "SELECT COUNT(*) FROM information_schema.tables "
                    "WHERE table_schema = :db AND table_type = 'BASE TABLE'"
                ),
                {"db": settings.db_name},
            ).scalar()
    with readonly_engine().connect() as conn:
        out["readonly_ok"] = conn.execute(text("SELECT 1")).scalar() == 1
    return out
