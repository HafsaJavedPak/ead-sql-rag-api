from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ead_api.core.config import Settings
from ead_api.core.cursors import decode_cursor, encode_cursor
from ead_api.errors import ApiError
from ead_api.models import Conversation, Message, User, utcnow
from ead_api.schemas import ConversationResponse


async def owned_conversation(
    session: AsyncSession,
    conversation_id: uuid.UUID,
    owner_user_id: uuid.UUID,
    *,
    for_update: bool = False,
) -> Conversation:
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.owner_user_id == owner_user_id,
        Conversation.deleted_at.is_(None),
    )
    if for_update:
        statement = statement.with_for_update()
    conversation = await session.scalar(statement)
    if conversation is None:
        raise ApiError(404, "conversation_not_found", "Conversation not found.", title="Not found")
    return conversation


async def conversation_response(
    session: AsyncSession, conversation: Conversation
) -> ConversationResponse:
    count = await session.scalar(
        select(func.count(Message.id)).where(
            Message.conversation_id == conversation.id,
            Message.deleted_at.is_(None),
        )
    )
    return ConversationResponse.model_validate(conversation).model_copy(
        update={"message_count": int(count or 0)}
    )


async def list_owned_conversations(
    session: AsyncSession,
    user: User,
    settings: Settings,
    *,
    limit: int,
    after: str | None,
    query: str | None = None,
) -> tuple[list[ConversationResponse], str | None]:
    statement = select(Conversation).where(
        Conversation.owner_user_id == user.id,
        Conversation.deleted_at.is_(None),
    )
    if query:
        statement = statement.where(Conversation.title.ilike(f"%{query.strip()}%"))
    if after:
        payload = decode_cursor(after, settings.jwt_secret_key)
        try:
            updated_at = datetime.fromisoformat(str(payload["updated_at"]))
            cursor_id = uuid.UUID(str(payload["id"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise ApiError(400, "invalid_cursor", "The pagination cursor is invalid.") from exc
        statement = statement.where(
            or_(
                Conversation.updated_at < updated_at,
                and_(Conversation.updated_at == updated_at, Conversation.id < cursor_id),
            )
        )
    rows = list(
        (
            await session.scalars(
                statement.order_by(Conversation.updated_at.desc(), Conversation.id.desc()).limit(
                    limit + 1
                )
            )
        ).all()
    )
    has_more = len(rows) > limit
    rows = rows[:limit]
    items = [await conversation_response(session, row) for row in rows]
    next_cursor = None
    if has_more and rows:
        last = rows[-1]
        next_cursor = encode_cursor(
            {"updated_at": last.updated_at.isoformat(), "id": str(last.id)},
            settings.jwt_secret_key,
        )
    return items, next_cursor


async def soft_delete_conversation(session: AsyncSession, conversation: Conversation) -> None:
    now = utcnow()
    conversation.deleted_at = now
    conversation.updated_at = now
    await session.commit()
