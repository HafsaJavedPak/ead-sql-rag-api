from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ead_api.errors import ApiError
from ead_api.models import AgentRun, Artifact, Conversation, Message
from ead_api.schemas import ArtifactResponse, MessageResponse, RunResponse


async def owned_message(
    session: AsyncSession, message_id: uuid.UUID, owner_user_id: uuid.UUID
) -> Message:
    message = await session.scalar(
        select(Message)
        .join(Conversation, Conversation.id == Message.conversation_id)
        .where(
            Message.id == message_id,
            Message.deleted_at.is_(None),
            Conversation.owner_user_id == owner_user_id,
            Conversation.deleted_at.is_(None),
        )
    )
    if message is None:
        raise ApiError(404, "message_not_found", "Message not found.", title="Not found")
    return message


async def run_response(session: AsyncSession, run: AgentRun, api_prefix: str) -> RunResponse:
    artifacts = list(
        (await session.scalars(select(Artifact).where(Artifact.run_id == run.id))).all()
    )
    artifact_responses = [
        ArtifactResponse(
            id=item.id,
            kind=item.kind,
            mime_type=item.mime_type,
            url=f"{api_prefix}/artifacts/{item.id}",
        )
        for item in artifacts
    ]
    return RunResponse.model_validate(run).model_copy(update={"artifacts": artifact_responses})


async def message_response(
    session: AsyncSession, message: Message, api_prefix: str
) -> MessageResponse:
    run = await session.scalar(select(AgentRun).where(AgentRun.assistant_message_id == message.id))
    rendered_run = await run_response(session, run, api_prefix) if run is not None else None
    return MessageResponse.model_validate(message).model_copy(update={"run": rendered_run})
