from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from ead_api.core.config import Settings
from ead_api.dependencies import AuthContext, get_auth_context, get_session, get_settings_from_app
from ead_api.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenPair,
    UserResponse,
)
from ead_api.services.auth import (
    login_user,
    refresh_session,
    register_user,
    revoke_all_sessions,
    revoke_session,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings_from_app),
) -> RegisterResponse:
    user, tokens = await register_user(session, payload, settings)
    response.headers["Cache-Control"] = "no-store"
    return RegisterResponse(user=UserResponse.model_validate(user), tokens=tokens)


@router.post("/jwt/login", response_model=TokenPair)
async def login(
    payload: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings_from_app),
) -> TokenPair:
    response.headers["Cache-Control"] = "no-store"
    return await login_user(session, payload, settings)


@router.post("/jwt/refresh", response_model=TokenPair)
async def refresh(
    payload: RefreshRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings_from_app),
) -> TokenPair:
    response.headers["Cache-Control"] = "no-store"
    return await refresh_session(session, payload, settings)


@router.post("/jwt/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    context: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_session),
) -> None:
    current = await session.get(type(context.auth_session), context.auth_session.id)
    if current is not None:
        await revoke_session(session, current, "logout")


@router.post("/jwt/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    context: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_session),
) -> None:
    await revoke_all_sessions(session, context.user.id, "logout_all")
