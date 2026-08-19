from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Header, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from ead_api.core.config import Settings
from ead_api.dependencies import (
    get_chat_service,
    get_current_user,
    get_session,
    get_settings_from_app,
)
from ead_api.errors import ApiError
from ead_api.models import Message, User, utcnow
from ead_api.schemas import ChatRequest, ChatResponse, MessagePage, MessageResponse
from ead_api.services.chat import ChatService
from ead_api.services.conversations import owned_conversation
from ead_api.services.messages import message_response, owned_message

conversation_router = APIRouter(prefix="/conversations", tags=["messages"])
message_router = APIRouter(prefix="/messages", tags=["messages"])


@conversation_router.get("/{conversation_id}/messages", response_model=MessagePage)
async def list_messages(
    conversation_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=100),
    after_sequence: int | None = Query(default=None, ge=0),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings_from_app),
) -> MessagePage:
    await owned_conversation(session, conversation_id, user.id)
    statement = select(Message).where(
        Message.conversation_id == conversation_id,
        Message.deleted_at.is_(None),
    )
    if after_sequence is not None:
        statement = statement.where(Message.sequence_no > after_sequence)
    rows = list(
        (
            await session.scalars(statement.order_by(Message.sequence_no.asc()).limit(limit + 1))
        ).all()
    )
    has_more = len(rows) > limit
    rows = rows[:limit]
    return MessagePage(
        items=[await message_response(session, row, settings.api_v1_prefix) for row in rows],
        next_cursor=str(rows[-1].sequence_no) if has_more and rows else None,
    )


@message_router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings_from_app),
) -> MessageResponse:
    message = await owned_message(session, message_id, user.id)
    return await message_response(session, message, settings.api_v1_prefix)


@message_router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    message = await owned_message(session, message_id, user.id)
    message.deleted_at = utcnow()
    await session.commit()


@conversation_router.post("/{conversation_id}/messages", response_model=ChatResponse)
async def create_chat_message(
    conversation_id: uuid.UUID,
    payload: ChatRequest,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    turn = await chat_service.prepare_turn(
        user_id=user.id,
        conversation_id=conversation_id,
        content=payload.content,
        request_id=request.state.request_id,
        idempotency_key=idempotency_key,
    )
    return await chat_service.run_non_streaming(turn)


@conversation_router.post("/{conversation_id}/messages/stream")
async def stream_chat_message(
    conversation_id: uuid.UUID,
    payload: ChatRequest,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> EventSourceResponse:
    turn = await chat_service.prepare_turn(
        user_id=user.id,
        conversation_id=conversation_id,
        content=payload.content,
        request_id=request.state.request_id,
        idempotency_key=idempotency_key,
    )

    async def events() -> AsyncIterator[dict[str, str]]:
        event_id = 1

        def event(name: str, data: dict) -> dict[str, str]:
            nonlocal event_id
            payload = {
                "id": str(event_id),
                "event": name,
                "data": json.dumps(data, separators=(",", ":"), default=str),
            }
            event_id += 1
            return payload

        yield event(
            "message.accepted",
            {
                "run_id": str(turn.run_id),
                "user_message_id": str(turn.user_message_id),
                "assistant_message_id": str(turn.assistant_message_id),
                "replay": turn.replay,
            },
        )
        if turn.replay:
            response = await chat_service.response(turn)
            yield event("message.completed", response.assistant_message.model_dump(mode="json"))
            return
        yield event("run.started", {"run_id": str(turn.run_id)})
        try:
            async for agent_event in chat_service.stream_turn(turn):
                if await request.is_disconnected():
                    await chat_service.cancel(turn.run_id, user.id)
                    return
                if agent_event.kind == "stage":
                    yield event("agent.stage", agent_event.data)
                elif agent_event.kind == "token":
                    yield event("assistant.delta", agent_event.data)
            response = await chat_service.response(turn)
            if response.assistant_message.status.value == "cancelled":
                yield event("run.cancelled", {"run_id": str(turn.run_id)})
                return
            run = response.assistant_message.run
            yield event(
                "result.ready",
                {
                    "run_id": str(turn.run_id),
                    "row_count": run.row_count if run else 0,
                    "truncated": run.truncated if run else False,
                    "artifacts": [
                        item.model_dump(mode="json") for item in (run.artifacts if run else [])
                    ],
                },
            )
            yield event("message.completed", response.assistant_message.model_dump(mode="json"))
        except ApiError as exc:
            yield event(
                "run.failed",
                {
                    "run_id": str(turn.run_id),
                    "request_id": turn.request_id,
                    "code": exc.code,
                    "detail": exc.detail,
                },
            )

    return EventSourceResponse(
        events(),
        ping=15,
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
        },
    )
