from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from ead_api.agent.runner import AgentEvent
from ead_api.core.config import Settings
from ead_api.main import create_app

PNG_1X1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c6360f8cfc000000301010018dd8db10000000049454e44"
    "ae426082"
)


class FakeRunner:
    def __init__(self, chart_path: Path) -> None:
        self.chart_path = chart_path
        self.histories: list[list[Any]] = []

    async def stream(self, **kwargs: Any):
        self.histories.append(list(kwargs["history"]))
        yield AgentEvent("stage", {"stage": "execute_sql"})
        yield AgentEvent("token", {"text": "There are "})
        yield AgentEvent("token", {"text": "42 projects."})
        yield AgentEvent(
            "result",
            {
                "answer": "There are 42 projects.",
                "validated_sql": "SELECT COUNT(*) AS project_count FROM wq_projects LIMIT 200",
                "selected_tables": ["wq_projects"],
                "columns": ["project_count"],
                "rows": [[42]],
                "retry_count": 0,
                "chart_path": str(self.chart_path),
            },
        )


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        app_env="test",
        app_database_url=f"sqlite+aiosqlite:///{tmp_path / 'app.db'}",
        auto_create_schema=True,
        jwt_secret_key="test-secret-that-is-long-enough-for-repeatable-api-tests",
        artifact_dir=tmp_path / "artifacts",
        langfuse_enabled=False,
    )


def _register(client: TestClient, email: str) -> dict[str, Any]:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "correct-horse-battery-staple"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _headers(registration: dict[str, Any]) -> dict[str, str]:
    return {"Authorization": f"Bearer {registration['tokens']['access_token']}"}


def _parse_sse(body: str) -> list[tuple[str, dict[str, Any]]]:
    events: list[tuple[str, dict[str, Any]]] = []
    name: str | None = None
    data: str | None = None
    for line in body.splitlines() + [""]:
        if line.startswith("event: "):
            name = line.removeprefix("event: ")
        elif line.startswith("data: "):
            data = line.removeprefix("data: ")
        elif not line and name is not None and data is not None:
            events.append((name, json.loads(data)))
            name = None
            data = None
    return events


def test_auth_refresh_rotation_and_duplicate_email(tmp_path: Path) -> None:
    app = create_app(_settings(tmp_path))
    with TestClient(app) as client:
        registration = _register(client, "Owner@example.com")
        duplicate = client.post(
            "/api/v1/auth/register",
            json={"email": "owner@example.com", "password": "correct-horse-battery-staple"},
        )
        assert duplicate.status_code == 409
        assert duplicate.json()["code"] == "email_exists"

        refreshed = client.post(
            "/api/v1/auth/jwt/refresh",
            json={"refresh_token": registration["tokens"]["refresh_token"]},
        )
        assert refreshed.status_code == 200
        assert refreshed.json()["refresh_token"] != registration["tokens"]["refresh_token"]

        replay = client.post(
            "/api/v1/auth/jwt/refresh",
            json={"refresh_token": registration["tokens"]["refresh_token"]},
        )
        assert replay.status_code == 401
        assert replay.json()["code"] == "refresh_token_reuse"


def test_chat_stream_idempotency_artifact_and_tenant_isolation(tmp_path: Path) -> None:
    chart = tmp_path / "chart.png"
    chart.write_bytes(PNG_1X1)
    app = create_app(_settings(tmp_path))

    with TestClient(app) as client:
        app.state.chat_service.runner = FakeRunner(chart)
        owner = _register(client, "owner@example.com")
        other = _register(client, "other@example.com")
        owner_headers = _headers(owner)
        other_headers = _headers(other)

        created = client.post(
            "/api/v1/conversations",
            headers=owner_headers,
            json={"title": "Portfolio totals"},
        )
        assert created.status_code == 201
        conversation_id = created.json()["id"]

        hidden = client.get(f"/api/v1/conversations/{conversation_id}", headers=other_headers)
        assert hidden.status_code == 404

        stream_headers = {**owner_headers, "Idempotency-Key": "portfolio-total-1"}
        with client.stream(
            "POST",
            f"/api/v1/conversations/{conversation_id}/messages/stream",
            headers=stream_headers,
            json={"content": "How many projects are there?"},
        ) as response:
            assert response.status_code == 200
            events = _parse_sse(response.read().decode())

        names = [name for name, _ in events]
        assert names == [
            "message.accepted",
            "run.started",
            "agent.stage",
            "assistant.delta",
            "assistant.delta",
            "result.ready",
            "message.completed",
        ]
        completed = events[-1][1]
        assert completed["content"] == "There are 42 projects."
        assert completed["run"]["row_count"] == 1
        artifact = completed["run"]["artifacts"][0]

        image = client.get(artifact["url"], headers=owner_headers)
        assert image.status_code == 200
        assert image.headers["content-type"] == "image/png"
        assert client.get(artifact["url"], headers=other_headers).status_code == 404

        replay = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            headers=stream_headers,
            json={"content": "How many projects are there?"},
        )
        assert replay.status_code == 200
        assert replay.json()["assistant_message"]["id"] == completed["id"]

        conflict = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            headers=stream_headers,
            json={"content": "A different question"},
        )
        assert conflict.status_code == 409
        assert conflict.json()["code"] == "idempotency_conflict"

        messages = client.get(
            f"/api/v1/conversations/{conversation_id}/messages", headers=owner_headers
        )
        assert messages.status_code == 200
        assert len(messages.json()["items"]) == 2


def test_non_streaming_chat_and_request_id(tmp_path: Path) -> None:
    chart = tmp_path / "chart.png"
    chart.write_bytes(PNG_1X1)
    app = create_app(_settings(tmp_path))

    with TestClient(app) as client:
        runner = FakeRunner(chart)
        app.state.chat_service.runner = runner
        registration = _register(client, "user@example.com")
        headers = {**_headers(registration), "X-Request-ID": "client-request-123"}
        conversation = client.post(
            "/api/v1/conversations",
            headers=headers,
            json={"title": "Totals"},
        ).json()
        response = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers=headers,
            json={"content": "Count projects"},
        )
        assert response.status_code == 200, response.text
        assert response.headers["x-request-id"] == "client-request-123"
        assert response.json()["assistant_message"]["run"]["status"] == "completed"

        follow_up = client.post(
            f"/api/v1/conversations/{conversation['id']}/messages",
            headers=headers,
            json={"content": "How does that compare?"},
        )
        assert follow_up.status_code == 200, follow_up.text
        assert runner.histories[0] == []
        assert [message.content for message in runner.histories[1]] == [
            "Count projects",
            "There are 42 projects.",
        ]
