"""The SELECT-only guard is a security boundary; it gets its own tests."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ead_agent.nodes.validate_sql import GuardError, guard  # noqa: E402

MUST_REJECT = [
    "INSERT INTO wq_donors (donor_name) VALUES ('x')",
    "UPDATE wq_donors SET donor_name = 'x' WHERE donor_id = 1",
    "DELETE FROM wq_donors",
    "DROP TABLE wq_donors",
    "ALTER TABLE wq_donors ADD COLUMN x INT",
    "TRUNCATE TABLE wq_donors",
    "CREATE TABLE zzz (a INT)",
    "GRANT ALL ON ead_db.* TO 'x'@'%'",
    # multi-statement / stacked injection
    "SELECT 1; DROP TABLE wq_donors",
    "SELECT 1; DELETE FROM wq_projects",
    # exfiltration
    "SELECT * FROM wq_donors INTO OUTFILE '/tmp/x.csv'",
    "SET GLOBAL general_log = 1",
    "",
    "   ",
    "not sql at all",
]

MUST_ACCEPT = [
    "SELECT 1",
    "SELECT donor_name FROM wq_donors LIMIT 5",
    "SELECT COUNT(*) AS n FROM wq_projects",
    """SELECT d.donor_name, COUNT(*) AS n
       FROM wq_donors d
       JOIN project_to_foreigncecomponents f ON d.donor_id = f.donor_id
       GROUP BY d.donor_name ORDER BY n DESC LIMIT 10""",
    "WITH t AS (SELECT 1 AS a) SELECT a FROM t",
]


@pytest.mark.parametrize("sql", MUST_REJECT)
def test_rejects(sql):
    with pytest.raises(GuardError):
        guard(sql)


@pytest.mark.parametrize("sql", MUST_ACCEPT)
def test_accepts(sql):
    assert "select" in guard(sql).lower()


def test_limit_is_injected_when_missing():
    out = guard("SELECT donor_name FROM wq_donors")
    assert "LIMIT" in out.upper()


def test_existing_limit_is_respected():
    out = guard("SELECT donor_name FROM wq_donors LIMIT 7")
    assert "LIMIT 7" in out.upper().replace("\n", " ")


def test_markdown_fences_are_stripped():
    out = guard("```sql\nSELECT 1\n```")
    assert out.upper().startswith("SELECT")


def test_string_literal_containing_keyword_is_not_rejected():
    # 'Project Update' contains 'update' but is data, not a statement.
    out = guard("SELECT project_name FROM wq_projects WHERE project_name = 'Project Update'")
    assert "SELECT" in out.upper()
