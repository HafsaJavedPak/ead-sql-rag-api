from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Any

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel, ValidationError

from ead_api.core.config import Settings

password_hash = PasswordHash.recommended()


class TokenClaims(BaseModel):
    sub: uuid.UUID
    sid: uuid.UUID
    jti: uuid.UUID
    type: str
    iss: str
    aud: str | list[str]
    iat: int
    nbf: int
    exp: int


class TokenValidationError(ValueError):
    pass


@lru_cache(maxsize=1)
def dummy_password_hash() -> str:
    return password_hash.hash("dummy-password-used-only-for-timing-equality")


def normalize_email(email: str) -> str:
    return email.strip().casefold()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    try:
        return password_hash.verify(password, encoded)
    except Exception:
        return False


def new_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str, settings: Settings) -> str:
    return hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def create_access_token(user_id: uuid.UUID, session_id: uuid.UUID, settings: Settings) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "sid": str(session_id),
        "jti": str(uuid.uuid4()),
        "type": "access",
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(minutes=settings.access_token_ttl_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> TokenClaims:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={"require": ["sub", "sid", "jti", "type", "iss", "aud", "iat", "nbf", "exp"]},
        )
        claims = TokenClaims.model_validate(payload)
    except (InvalidTokenError, ValidationError, ValueError, TypeError) as exc:
        raise TokenValidationError("Invalid access token") from exc
    if claims.type != "access":
        raise TokenValidationError("Invalid token type")
    return claims
