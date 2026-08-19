from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ead_api.dependencies import get_current_user, get_session
from ead_api.models import User
from ead_api.schemas import UserPatch, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def read_me(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserResponse)
async def patch_me(
    payload: UserPatch,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    persistent = await session.get(User, user.id)
    assert persistent is not None
    if payload.display_name is not None:
        persistent.display_name = payload.display_name
    await session.commit()
    await session.refresh(persistent)
    return UserResponse.model_validate(persistent)
