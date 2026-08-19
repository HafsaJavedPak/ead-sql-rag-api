"""The scope gate must refuse off-topic and write requests -- WITHOUT
refusing legitimate read questions that merely contain a scary word."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ead_agent.nodes.classify import WRITE_INTENT  # noqa: E402

MUST_MATCH_WRITE = [
    "delete all projects",
    "delete from wq_donors",
    "drop the table wq_projects",
    "drop table projects",
    "truncate the projects table",
    "insert a new donor called ABC",
    "insert into wq_donors values",
    "add a new row to the projects table",
    "add a new column for status",
    "update the status of project 5",
    "update all records",
    "alter the table to add a field",
    "create a new table for reports",
    "rename the column donor_name",
    "remove the row for project 12",
]

# These READ questions contain write-ish words and must NOT be caught.
MUST_NOT_MATCH_WRITE = [
    "show me recently updated projects",
    "which projects were dropped from the plan?",
    "list projects with the latest updated_at date",
    "how many donors are there?",
    "what is the total project cost by sector?",
    "which projects have no disbursement records?",
    "show the projected disbursement trend by fiscal year",
    "who are the top donors?",
    "add up the total cost by region",          # 'add up' is aggregation
    "show projects created in 2024",
]


@pytest.mark.parametrize("q", MUST_MATCH_WRITE)
def test_write_intent_detected(q):
    assert WRITE_INTENT.search(q), f"should be flagged as a write: {q!r}"


@pytest.mark.parametrize("q", MUST_NOT_MATCH_WRITE)
def test_read_questions_not_flagged(q):
    assert not WRITE_INTENT.search(q), f"read question wrongly flagged: {q!r}"
