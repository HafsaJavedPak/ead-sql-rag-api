from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ead_api.core.config import Settings
from ead_api.dependencies import get_current_user, get_session, get_settings_from_app
from ead_api.models import Conversation, User, utcnow
from ead_api.schemas import (
    ConversationCreate,
    ConversationPage,
    ConversationPatch,
    ConversationResponse,
)
from ead_api.services.conversations import (
    conversation_response,
    list_owned_conversations,
    owned_conversation,
    soft_delete_conversation,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=ConversationPage)
async def list_conversations(
    limit: int = Query(default=20, ge=1, le=100),
    after: str | None = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings_from_app),
) -> ConversationPage:
    items, next_cursor = await list_owned_conversations(
        session, user, settings, limit=limit, after=after
    )
    return ConversationPage(items=items, next_cursor=next_cursor)


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ConversationResponse:
    conversation = Conversation(owner_user_id=user.id, title=payload.title.strip())
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return await conversation_response(session, conversation)


@router.get("/search", response_model=ConversationPage)
async def search_conversations(
    q: str = Query(min_length=1, max_length=240),
    limit: int = Query(default=20, ge=1, le=100),
    after: str | None = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings_from_app),
) -> ConversationPage:
    items, next_cursor = await list_owned_conversations(
        session, user, settings, limit=limit, after=after, query=q
    )
    return ConversationPage(items=items, next_cursor=next_cursor)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ConversationResponse:
    conversation = await owned_conversation(session, conversation_id, user.id)
    return await conversation_response(session, conversation)


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def patch_conversation(
    conversation_id: uuid.UUID,
    payload: ConversationPatch,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ConversationResponse:
    conversation = await owned_conversation(session, conversation_id, user.id, for_update=True)
    if payload.title is not None:
        conversation.title = payload.title.strip()
    if payload.status is not None:
        conversation.status = payload.status
    conversation.updated_at = utcnow()
    await session.commit()
    await session.refresh(conversation)
    return await conversation_response(session, conversation)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    conversation = await owned_conversation(session, conversation_id, user.id, for_update=True)
    await soft_delete_conversation(session, conversation)
