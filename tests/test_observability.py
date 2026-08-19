from __future__ import annotations

from langfuse.types import MaskOtelSpansParams, OtelSpanData, OtelSpanIdentifier

from ead_api.core.observability import _otel_span_masker, _redact


def test_redact_nested_credentials_and_personal_data() -> None:
    payload = {
        "password": "do-not-export",
        "nested": {
            "authorization": "Bearer abc.def.ghi",
            "message": "Contact analyst@example.com",
        },
    }

    assert _redact(payload) == {
        "password": "[REDACTED]",
        "nested": {
            "authorization": "[REDACTED]",
            "message": "Contact [EMAIL_REDACTED]",
        },
    }


def test_otel_export_mask_removes_content_and_secrets() -> None:
    identifier = OtelSpanIdentifier(trace_id="trace", span_id="span")
    span = OtelSpanData(
        trace_id="trace",
        span_id="span",
        parent_span_id=None,
        name="chat",
        instrumentation_scope_name="test",
        instrumentation_scope_version="1",
        attributes={
            "gen_ai.prompt": "private question",
            "http.request.header.authorization": "Bearer abc.def.ghi",
            "service.version": "1.2.3",
            "user.note": "analyst@example.com",
        },
        resource_attributes={},
    )

    result = _otel_span_masker(False)(MaskOtelSpansParams(spans={identifier: span}))
    patch = result.span_patches[identifier]

    assert patch is not None
    assert patch.set_attributes["gen_ai.prompt"] == "[CONTENT_REDACTED]"
    assert patch.set_attributes["http.request.header.authorization"] == "[REDACTED]"
    assert patch.set_attributes["user.note"] == "[EMAIL_REDACTED]"
    assert "service.version" not in patch.set_attributes


def test_otel_export_mask_retains_approved_content_after_pii_redaction() -> None:
    identifier = OtelSpanIdentifier(trace_id="trace", span_id="span")
    span = OtelSpanData(
        trace_id="trace",
        span_id="span",
        parent_span_id=None,
        name="chat",
        instrumentation_scope_name=None,
        instrumentation_scope_version=None,
        attributes={"gen_ai.prompt": "Question from analyst@example.com"},
        resource_attributes={},
    )

    result = _otel_span_masker(True)(MaskOtelSpansParams(spans={identifier: span}))
    patch = result.span_patches[identifier]

    assert patch is not None
    assert patch.set_attributes["gen_ai.prompt"] == "Question from [EMAIL_REDACTED]"
