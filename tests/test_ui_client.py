from __future__ import annotations

import json

import httpx

from ead_ui.client import EadApiClient, UiSession


def test_register_and_conversation_journey() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/auth/register"):
            return httpx.Response(
                201,
                json={
                    "user": {"id": "user-1", "email": "user@example.com"},
                    "tokens": {
                        "access_token": "access",
                        "refresh_token": "refresh",
                        "token_type": "bearer",
                        "expires_in": 900,
                    },
                },
            )
        if request.url.path == "/api/v1/conversations":
            assert request.headers["authorization"] == "Bearer access"
            return httpx.Response(201, json={"id": "conversation-1", "title": "Test"})
        raise AssertionError(f"Unexpected request: {request.method} {request.url}")

    client = EadApiClient("http://api.test", transport=httpx.MockTransport(handler))
    session = UiSession()

    user = client.register("user@example.com", "long-enough-password", "User", session)
    conversation = client.create_conversation("Test", session)

    assert user["email"] == "user@example.com"
    assert session.authenticated
    assert session.conversation_id == "conversation-1"
    assert conversation["title"] == "Test"
    assert len(requests) == 2


def test_expired_access_token_is_refreshed_once() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if request.url.path.endswith("/users/me") and len(calls) == 1:
            return httpx.Response(401, json={"detail": "expired"})
        if request.url.path.endswith("/auth/jwt/refresh"):
            return httpx.Response(
                200,
                json={
                    "access_token": "new-access",
                    "refresh_token": "new-refresh",
                    "token_type": "bearer",
                    "expires_in": 900,
                },
            )
        if request.url.path.endswith("/users/me"):
            assert request.headers["authorization"] == "Bearer new-access"
            return httpx.Response(200, json={"id": "user-1", "email": "user@example.com"})
        raise AssertionError(f"Unexpected request: {request.method} {request.url}")

    client = EadApiClient("http://api.test", transport=httpx.MockTransport(handler))
    session = UiSession(access_token="expired", refresh_token="refresh")

    assert client.me(session)["id"] == "user-1"
    assert session.access_token == "new-access"
    assert calls == [
        "/api/v1/users/me",
        "/api/v1/auth/jwt/refresh",
        "/api/v1/users/me",
    ]


def test_streaming_sse_and_protected_artifact() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer access"
        if request.url.path.endswith("/messages/stream"):
            events = [
                ("agent.stage", {"stage": "execute_sql"}),
                ("assistant.delta", {"text": "Hello"}),
                ("message.completed", {"content": "Hello", "run": None}),
            ]
            body = "".join(
                f"event: {name}\ndata: {json.dumps(data)}\n\n" for name, data in events
            )
            return httpx.Response(200, text=body, headers={"content-type": "text/event-stream"})
        if request.url.path.endswith("/artifacts/chart-1"):
            return httpx.Response(200, content=b"png", headers={"content-type": "image/png"})
        raise AssertionError(f"Unexpected request: {request.method} {request.url}")

    client = EadApiClient("http://api.test", transport=httpx.MockTransport(handler))
    session = UiSession(access_token="access", refresh_token="refresh")

    events = list(client.stream_chat("conversation-1", "Question", session))
    content, mime_type = client.artifact("/api/v1/artifacts/chart-1", session)

    assert [event["event"] for event in events] == [
        "agent.stage",
        "assistant.delta",
        "message.completed",
    ]
    assert events[1]["data"] == {"text": "Hello"}
    assert (content, mime_type) == (b"png", "image/png")


def test_gradio_ui_builds() -> None:
    from ead_ui.app import demo

    component_types = {component["type"] for component in demo.config["components"]}
    assert {"chatbot", "dataframe", "image", "code"}.issubset(component_types)
