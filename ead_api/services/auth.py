from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ead_api.core.config import Settings
from ead_api.core.security import (
    create_access_token,
    dummy_password_hash,
    hash_password,
    hash_refresh_token,
    new_refresh_token,
    normalize_email,
    verify_password,
)
from ead_api.errors import ApiError
from ead_api.models import AuthSession, User
from ead_api.schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenPair


def _token_pair(
    user: User, auth_session: AuthSession, refresh: str, settings: Settings
) -> TokenPair:
    return TokenPair(
        access_token=create_access_token(user.id, auth_session.id, settings),
        refresh_token=refresh,
        expires_in=settings.access_token_ttl_minutes * 60,
    )


async def register_user(
    session: AsyncSession, payload: RegisterRequest, settings: Settings
) -> tuple[User, TokenPair]:
    refresh = new_refresh_token()
    user = User(
        email=str(payload.email).strip(),
        email_normalized=normalize_email(str(payload.email)),
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
    )
    session.add(user)
    try:
        await session.flush()
        auth_session = AuthSession(
            user_id=user.id,
            token_family_id=uuid.uuid4(),
            refresh_token_hash=hash_refresh_token(refresh, settings),
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_ttl_days),
        )
        session.add(auth_session)
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise ApiError(409, "email_exists", "An account with this email already exists.") from exc
    await session.refresh(user)
    await session.refresh(auth_session)
    return user, _token_pair(user, auth_session, refresh, settings)


async def login_user(session: AsyncSession, payload: LoginRequest, settings: Settings) -> TokenPair:
    normalized = normalize_email(str(payload.email))
    user = await session.scalar(select(User).where(User.email_normalized == normalized))
    encoded = user.password_hash if user is not None else dummy_password_hash()
    valid = verify_password(payload.password, encoded)
    if user is None or not valid or not user.is_active:
        raise ApiError(
            401,
            "invalid_credentials",
            "The email or password is incorrect.",
            title="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )

    refresh = new_refresh_token()
    auth_session = AuthSession(
        user_id=user.id,
        token_family_id=uuid.uuid4(),
        refresh_token_hash=hash_refresh_token(refresh, settings),
        expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_ttl_days),
    )
    user.last_login_at = datetime.now(UTC)
    session.add(auth_session)
    await session.commit()
    await session.refresh(auth_session)
    return _token_pair(user, auth_session, refresh, settings)


async def refresh_session(
    session: AsyncSession, payload: RefreshRequest, settings: Settings
) -> TokenPair:
    digest = hash_refresh_token(payload.refresh_token, settings)
    auth_session = await session.scalar(
        select(AuthSession)
        .where(
            or_(
                AuthSession.refresh_token_hash == digest,
                AuthSession.previous_refresh_token_hash == digest,
            )
        )
        .with_for_update()
    )
    if auth_session is None:
        raise ApiError(401, "invalid_refresh_token", "The refresh token is invalid.")

    now = datetime.now(UTC)
    expires_at = auth_session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    replayed = auth_session.previous_refresh_token_hash == digest
    if replayed:
        await session.execute(
            update(AuthSession)
            .where(AuthSession.token_family_id == auth_session.token_family_id)
            .values(revoked_at=now, revoke_reason="refresh_token_reuse")
        )
        await session.commit()
        raise ApiError(401, "refresh_token_reuse", "The refresh-token family was revoked.")
    if auth_session.revoked_at is not None or expires_at <= now:
        raise ApiError(401, "invalid_refresh_token", "The refresh token is invalid or expired.")

    user = await session.get(User, auth_session.user_id)
    if user is None or not user.is_active:
        raise ApiError(401, "invalid_refresh_token", "The refresh token is invalid.")

    new_token = new_refresh_token()
    auth_session.previous_refresh_token_hash = auth_session.refresh_token_hash
    auth_session.refresh_token_hash = hash_refresh_token(new_token, settings)
    auth_session.last_used_at = now
    await session.commit()
    return _token_pair(user, auth_session, new_token, settings)


async def revoke_session(session: AsyncSession, auth_session: AuthSession, reason: str) -> None:
    auth_session.revoked_at = datetime.now(UTC)
    auth_session.revoke_reason = reason
    await session.commit()


async def revoke_all_sessions(session: AsyncSession, user_id: uuid.UUID, reason: str) -> None:
    await session.execute(
        update(AuthSession)
        .where(AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC), revoke_reason=reason)
    )
    await session.commit()
