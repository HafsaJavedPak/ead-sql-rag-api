"""Fail fast when a production environment file is incomplete or unsafe."""

from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import dotenv_values

from ead_api.core.config import Settings

REQUIRED_SECRETS = {
    "APP_POSTGRES_PASSWORD",
    "JWT_SECRET_KEY",
    "LANGFUSE_CLICKHOUSE_PASSWORD",
    "LANGFUSE_ENCRYPTION_KEY",
    "LANGFUSE_INIT_PROJECT_PUBLIC_KEY",
    "LANGFUSE_INIT_PROJECT_SECRET_KEY",
    "LANGFUSE_INIT_USER_PASSWORD",
    "LANGFUSE_MINIO_PASSWORD",
    "LANGFUSE_NEXTAUTH_SECRET",
    "LANGFUSE_POSTGRES_PASSWORD",
    "LANGFUSE_REDIS_AUTH",
    "LANGFUSE_SALT",
    "MYSQL_READONLY_PASSWORD",
    "MYSQL_ROOT_PASSWORD",
}
PLACEHOLDER_PARTS = {"change-me", "replace", "example.local"}


def validate(path: Path) -> list[str]:
    values = {key: value or "" for key, value in dotenv_values(path).items()}
    problems = []
    for key in sorted(REQUIRED_SECRETS):
        value = values.get(key, "")
        if not value:
            problems.append(f"{key} is missing")
        elif any(part in value.lower() for part in PLACEHOLDER_PARTS):
            problems.append(f"{key} still contains a placeholder")
    try:
        Settings.model_validate({key.lower(): value for key, value in values.items()})
    except ValueError as exc:
        problems.append(f"API settings are invalid: {exc}")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("env_file", type=Path, nargs="?", default=Path(".env.production"))
    args = parser.parse_args()
    if not args.env_file.is_file():
        raise SystemExit(f"Environment file not found: {args.env_file}")
    problems = validate(args.env_file)
    if problems:
        print("Production configuration failed:")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)
    print(f"Production configuration is valid: {args.env_file}")


if __name__ == "__main__":
    main()
