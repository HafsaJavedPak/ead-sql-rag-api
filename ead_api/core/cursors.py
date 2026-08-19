from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any

from ead_api.errors import ApiError


def encode_cursor(payload: dict[str, Any], secret: str) -> str:
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(raw + signature).decode("ascii").rstrip("=")


def decode_cursor(value: str, secret: str) -> dict[str, Any]:
    try:
        padded = value + "=" * (-len(value) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode("ascii"))
        raw, signature = decoded[:-32], decoded[-32:]
        expected = hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError("signature mismatch")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("cursor is not an object")
        return payload
    except Exception as exc:
        raise ApiError(400, "invalid_cursor", "The pagination cursor is invalid.") from exc
