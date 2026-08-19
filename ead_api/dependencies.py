from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ead_api.core.config import Settings
from ead_api.core.security import TokenValidationError, decode_access_token
from ead_api.db.base import Database
from ead_api.errors import ApiError
from ead_api.models import AuthSession, User
from ead_api.services.chat import ChatService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/jwt/login")


@dataclass(frozen=True)
class AuthContext:
    user: User
    auth_session: AuthSession


def get_database(request: Request) -> Database:
    return request.app.state.database


def get_settings_from_app(request: Request) -> Settings:
    return request.app.state.settings


def get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service


async def get_session(database: Database = Depends(get_database)) -> AsyncIterator[AsyncSession]:
    async with database.session_factory() as session:
        yield session


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


async def get_auth_context(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings_from_app),
) -> AuthContext:
    unauthorized = ApiError(
        401,
        "invalid_token",
        "Authentication is required.",
        title="Unauthorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        claims = decode_access_token(token, settings)
    except TokenValidationError as exc:
        raise unauthorized from exc

    auth_session = await session.get(AuthSession, claims.sid)
    if (
        auth_session is None
        or auth_session.user_id != claims.sub
        or auth_session.revoked_at is not None
        or _aware(auth_session.expires_at) <= datetime.now(UTC)
    ):
        raise unauthorized

    user = await session.get(User, claims.sub)
    if user is None or not user.is_active:
        raise unauthorized
    return AuthContext(user=user, auth_session=auth_session)


async def get_current_user(context: AuthContext = Depends(get_auth_context)) -> User:
    return context.user
