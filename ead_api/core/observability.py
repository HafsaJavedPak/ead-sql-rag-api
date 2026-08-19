from __future__ import annotations

import re
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

from ead_api.core.config import Settings

EMAIL = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
BEARER = re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+")
SECRET_ATTRIBUTE_PARTS = {
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "password",
    "refresh_token",
    "secret",
    "token",
}
CONTENT_ATTRIBUTE_PARTS = {
    "completion",
    "content",
    "input",
    "message",
    "output",
    "prompt",
}


def _redact(data: Any) -> Any:
    if isinstance(data, str):
        return BEARER.sub("Bearer [REDACTED]", EMAIL.sub("[EMAIL_REDACTED]", data))
    if isinstance(data, dict):
        return {
            key: "[REDACTED]"
            if key.lower()
            in {"password", "token", "access_token", "refresh_token", "authorization"}
            else _redact(value)
            for key, value in data.items()
        }
    if isinstance(data, list):
        return [_redact(item) for item in data]
    if isinstance(data, tuple):
        return [_redact(item) for item in data]
    return data


def _attribute_is_sensitive(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return any(part in normalized for part in SECRET_ATTRIBUTE_PARTS)


def _attribute_contains_content(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return any(part in normalized for part in CONTENT_ATTRIBUTE_PARTS)


def _otel_span_masker(capture_content: bool) -> Any:
    from langfuse.types import MaskOtelSpansResult, OtelSpanPatch

    def mask_spans(params: Any) -> Any:
        patches: dict[Any, Any] = {}
        for identifier, span in params.spans.items():
            replacements: dict[str, Any] = {}
            for key, value in span.attributes.items():
                if _attribute_is_sensitive(key):
                    replacements[key] = "[REDACTED]"
                elif not capture_content and _attribute_contains_content(key):
                    replacements[key] = "[CONTENT_REDACTED]"
                elif isinstance(value, str):
                    redacted = _redact(value)
                    if redacted != value:
                        replacements[key] = redacted
            if replacements:
                patches[identifier] = OtelSpanPatch(set_attributes=replacements)
        return MaskOtelSpansResult(span_patches=patches)

    return mask_spans


@dataclass(frozen=True)
class TraceScope:
    callbacks: list[Any]
    trace_id: str | None


class Observability:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client: Any | None = None
        if not settings.langfuse_enabled:
            return
        from langfuse import Langfuse

        def mask(data: Any, **_: Any) -> Any:
            if not settings.langfuse_capture_content:
                return "[CONTENT_REDACTED]"
            return _redact(data)

        self.client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            base_url=settings.langfuse_base_url,
            environment=settings.langfuse_tracing_environment,
            sample_rate=settings.langfuse_sample_rate,
            mask=mask,
            mask_otel_spans=_otel_span_masker(settings.langfuse_capture_content),
        )

    @contextmanager
    def chat_trace(
        self,
        *,
        user_id: str,
        conversation_id: str,
        request_id: str,
        run_id: str,
        question: str,
    ) -> Iterator[TraceScope]:
        if self.client is None:
            yield TraceScope(callbacks=[], trace_id=None)
            return

        from langfuse import propagate_attributes
        from langfuse.langchain import CallbackHandler

        handler = CallbackHandler()
        with propagate_attributes(
            user_id=user_id,
            session_id=conversation_id,
            tags=["sql-rag", self.settings.app_env],
            metadata={
                "request_id": request_id,
                "run_id": run_id,
                "api_version": "v1",
            },
        ):
            with self.client.start_as_current_observation(
                as_type="span",
                name="api.chat-turn",
                input=question if self.settings.langfuse_capture_content else None,
            ):
                trace_id = self.client.get_current_trace_id()
                yield TraceScope(callbacks=[handler], trace_id=trace_id)

    def shutdown(self) -> None:
        if self.client is not None:
            try:
                self.client.shutdown()
            except Exception:
                pass
