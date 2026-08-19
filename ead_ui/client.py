from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

import httpx


class ApiClientError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass
class UiSession:
    access_token: str = ""
    refresh_token: str = ""
    user: dict[str, Any] = field(default_factory=dict)
    conversation_id: str = ""

    @property
    def authenticated(self) -> bool:
        return bool(self.access_token and self.refresh_token)

    def clear(self) -> None:
        self.access_token = ""
        self.refresh_token = ""
        self.user = {}
        self.conversation_id = ""


class EadApiClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 180.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.transport = transport

    def _client(self) -> httpx.Client:
        return httpx.Client(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout, connect=10.0),
            transport=self.transport,
        )

    @staticmethod
    def _detail(response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return response.text.strip() or f"HTTP {response.status_code}"
        if isinstance(payload, dict):
            return str(payload.get("detail") or payload.get("message") or payload)
        return str(payload)

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.is_error:
            raise ApiClientError(
                self._detail(response),
                status_code=response.status_code,
            )

    @staticmethod
    def _headers(session: UiSession) -> dict[str, str]:
        return {"Authorization": f"Bearer {session.access_token}"}

    @staticmethod
    def _apply_tokens(session: UiSession, tokens: dict[str, Any]) -> None:
        session.access_token = str(tokens["access_token"])
        session.refresh_token = str(tokens["refresh_token"])

    def register(
        self, email: str, password: str, display_name: str, session: UiSession
    ) -> dict[str, Any]:
        with self._client() as client:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": password,
                    "display_name": display_name.strip() or None,
                },
            )
        self._raise_for_status(response)
        payload = response.json()
        self._apply_tokens(session, payload["tokens"])
        session.user = payload["user"]
        return session.user

    def login(self, email: str, password: str, session: UiSession) -> dict[str, Any]:
        with self._client() as client:
            response = client.post(
                "/api/v1/auth/jwt/login",
                json={"email": email, "password": password},
            )
        self._raise_for_status(response)
        self._apply_tokens(session, response.json())
        session.user = self.me(session)
        return session.user

    def refresh(self, session: UiSession) -> None:
        with self._client() as client:
            response = client.post(
                "/api/v1/auth/jwt/refresh",
                json={"refresh_token": session.refresh_token},
            )
        self._raise_for_status(response)
        self._apply_tokens(session, response.json())

    def _request(
        self,
        method: str,
        path: str,
        session: UiSession,
        *,
        json_body: dict[str, Any] | None = None,
        retry_auth: bool = True,
    ) -> httpx.Response:
        if not session.authenticated:
            raise ApiClientError("Register or sign in before using this action.")
        with self._client() as client:
            response = client.request(
                method,
                path,
                headers=self._headers(session),
                json=json_body,
            )
        if response.status_code == 401 and retry_auth:
            self.refresh(session)
            return self._request(
                method,
                path,
                session,
                json_body=json_body,
                retry_auth=False,
            )
        self._raise_for_status(response)
        return response

    def me(self, session: UiSession) -> dict[str, Any]:
        return self._request("GET", "/api/v1/users/me", session).json()

    def logout(self, session: UiSession) -> None:
        if session.authenticated:
            try:
                self._request("POST", "/api/v1/auth/jwt/logout", session)
            finally:
                session.clear()

    def list_conversations(self, session: UiSession) -> list[dict[str, Any]]:
        response = self._request("GET", "/api/v1/conversations?limit=100", session)
        return list(response.json()["items"])

    def create_conversation(self, title: str, session: UiSession) -> dict[str, Any]:
        response = self._request(
            "POST",
            "/api/v1/conversations",
            session,
            json_body={"title": title.strip() or "New conversation"},
        )
        conversation = response.json()
        session.conversation_id = str(conversation["id"])
        return conversation

    def messages(self, conversation_id: str, session: UiSession) -> list[dict[str, Any]]:
        response = self._request(
            "GET",
            f"/api/v1/conversations/{conversation_id}/messages?limit=100",
            session,
        )
        return list(response.json()["items"])

    def chat(self, conversation_id: str, content: str, session: UiSession) -> dict[str, Any]:
        response = self._request(
            "POST",
            f"/api/v1/conversations/{conversation_id}/messages",
            session,
            json_body={"content": content},
        )
        return response.json()

    @staticmethod
    def _sse_events(response: httpx.Response) -> Iterator[dict[str, Any]]:
        event_name = "message"
        data_lines: list[str] = []
        for line in response.iter_lines():
            if not line:
                if data_lines:
                    raw = "\n".join(data_lines)
                    try:
                        data = json.loads(raw)
                    except json.JSONDecodeError:
                        data = {"text": raw}
                    yield {"event": event_name, "data": data}
                event_name = "message"
                data_lines = []
            elif line.startswith("event:"):
                event_name = line[6:].strip()
            elif line.startswith("data:"):
                data_lines.append(line[5:].lstrip())
        if data_lines:
            raw = "\n".join(data_lines)
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = {"text": raw}
            yield {"event": event_name, "data": data}

    def stream_chat(
        self, conversation_id: str, content: str, session: UiSession
    ) -> Iterator[dict[str, Any]]:
        if not session.authenticated:
            raise ApiClientError("Register or sign in before using chat.")
        path = f"/api/v1/conversations/{conversation_id}/messages/stream"
        for attempt in range(2):
            with self._client() as client:
                with client.stream(
                    "POST",
                    path,
                    headers={**self._headers(session), "Accept": "text/event-stream"},
                    json={"content": content},
                ) as response:
                    if response.status_code == 401 and attempt == 0:
                        self.refresh(session)
                        continue
                    self._raise_for_status(response)
                    yield from self._sse_events(response)
                    return

    def artifact(self, url: str, session: UiSession) -> tuple[bytes, str]:
        response = self._request("GET", url, session)
        return response.content, response.headers.get("content-type", "application/octet-stream")
