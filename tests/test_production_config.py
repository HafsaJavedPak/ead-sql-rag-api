from __future__ import annotations

from pathlib import Path

from scripts.check_production_config import validate


def test_example_production_config_is_rejected_for_placeholders() -> None:
    problems = validate(Path(".env.production.example"))

    assert any("JWT_SECRET_KEY still contains a placeholder" in item for item in problems)
    assert any("MYSQL_ROOT_PASSWORD still contains a placeholder" in item for item in problems)
