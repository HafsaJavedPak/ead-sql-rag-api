from __future__ import annotations

import asyncio
import hashlib
import shutil
import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ead_api.agent.runner import AgentEvent, SqlAgentRunner, history_messages
from ead_api.core.config import Settings
from ead_api.core.observability import Observability
from ead_api.db.base import Database
from ead_api.errors import ApiError
from ead_api.models import (
    AgentRun,
    Artifact,
    Conversation,
    Message,
    MessageRole,
    MessageStatus,
    RunStatus,
    utcnow,
)
from ead_api.schemas import ChatResponse
from ead_api.services.conversations import owned_conversation
from ead_api.services.messages import message_response


@dataclass(frozen=True)
class PreparedTurn:
    run_id: uuid.UUID
    conversation_id: uuid.UUID
    user_id: uuid.UUID
    user_message_id: uuid.UUID
    assistant_message_id: uuid.UUID
    question: str
    request_id: str
    replay: bool = False


class TurnCancelled(Exception):
    pass


class ChatService:
    def __init__(
        self,
        database: Database,
        runner: SqlAgentRunner,
        observability: Observability,
        settings: Settings,
    ) -> None:
        self.database = database
        self.runner = runner
        self.observability = observability
        self.settings = settings

    @staticmethod
    def _request_hash(conversation_id: uuid.UUID, content: str) -> str:
        value = f"{conversation_id}:{content}".encode()
        return hashlib.sha256(value).hexdigest()

    async def prepare_turn(
        self,
        *,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        content: str,
        request_id: str,
        idempotency_key: str | None,
    ) -> PreparedTurn:
        if len(content) > self.settings.max_message_chars:
            raise ApiError(413, "message_too_large", "The message exceeds the configured limit.")
        if idempotency_key and len(idempotency_key) > 160:
            raise ApiError(400, "invalid_idempotency_key", "Idempotency-Key is too long.")
        request_hash = self._request_hash(conversation_id, content)

        async with self.database.session_factory() as session:
            if idempotency_key:
                existing = await session.scalar(
                    select(AgentRun).where(
                        AgentRun.owner_user_id == user_id,
                        AgentRun.idempotency_key == idempotency_key,
                    )
                )
                if existing is not None:
                    if existing.request_hash != request_hash:
                        raise ApiError(
                            409,
                            "idempotency_conflict",
                            "The idempotency key was already used with another request.",
                        )
                    return PreparedTurn(
                        run_id=existing.id,
                        conversation_id=existing.conversation_id,
                        user_id=existing.owner_user_id,
                        user_message_id=existing.user_message_id,
                        assistant_message_id=existing.assistant_message_id,
                        question=content,
                        request_id=existing.request_id,
                        replay=True,
                    )

            conversation = await owned_conversation(
                session, conversation_id, user_id, for_update=True
            )
            active = await session.scalar(
                select(AgentRun.id).where(
                    AgentRun.conversation_id == conversation_id,
                    AgentRun.status.in_([RunStatus.QUEUED, RunStatus.RUNNING]),
                )
            )
            if active is not None:
                raise ApiError(
                    409, "run_in_progress", "This conversation already has an active run."
                )

            maximum = await session.scalar(
                select(func.max(Message.sequence_no)).where(
                    Message.conversation_id == conversation_id
                )
            )
            user_message = Message(
                conversation_id=conversation_id,
                sequence_no=int(maximum or 0) + 1,
                role=MessageRole.USER,
                status=MessageStatus.COMPLETED,
                content=content,
                completed_at=utcnow(),
            )
            assistant_message = Message(
                conversation_id=conversation_id,
                sequence_no=int(maximum or 0) + 2,
                role=MessageRole.ASSISTANT,
                status=MessageStatus.PENDING,
                content="",
            )
            session.add_all([user_message, assistant_message])
            await session.flush()
            run = AgentRun(
                owner_user_id=user_id,
                conversation_id=conversation_id,
                user_message_id=user_message.id,
                assistant_message_id=assistant_message.id,
                request_id=request_id,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                status=RunStatus.QUEUED,
            )
            session.add(run)
            conversation.last_message_at = user_message.created_at
            conversation.updated_at = user_message.created_at
            try:
                await session.commit()
            except IntegrityError as exc:
                await session.rollback()
                raise ApiError(
                    409, "run_in_progress", "This conversation already has an active run."
                ) from exc
            return PreparedTurn(
                run_id=run.id,
                conversation_id=conversation_id,
                user_id=user_id,
                user_message_id=user_message.id,
                assistant_message_id=assistant_message.id,
                question=content,
                request_id=request_id,
            )

    async def _load_history(self, turn: PreparedTurn) -> list[tuple[str, str]]:
        async with self.database.session_factory() as session:
            user_message = await session.get(Message, turn.user_message_id)
            assert user_message is not None
            result = await session.execute(
                select(Message.role, Message.content)
                .where(
                    Message.conversation_id == turn.conversation_id,
                    Message.sequence_no < user_message.sequence_no,
                    Message.status == MessageStatus.COMPLETED,
                    Message.deleted_at.is_(None),
                )
                .order_by(Message.sequence_no.desc())
                .limit(self.settings.history_max_messages)
            )
            rows = list(result.all())
        rows.reverse()
        return [
            (role.value if hasattr(role, "value") else str(role), content) for role, content in rows
        ]

    async def _is_cancelled(self, run_id: uuid.UUID) -> bool:
        async with self.database.session_factory() as session:
            status = await session.scalar(select(AgentRun.status).where(AgentRun.id == run_id))
            return status == RunStatus.CANCELLED

    async def _set_running(self, run_id: uuid.UUID) -> None:
        async with self.database.session_factory() as session:
            run = await session.get(AgentRun, run_id)
            if run is None:
                raise ApiError(404, "run_not_found", "Run not found.", title="Not found")
            if run.status == RunStatus.CANCELLED:
                raise TurnCancelled
            run.status = RunStatus.RUNNING
            run.started_at = utcnow()
            await session.commit()

    async def _set_trace_id(self, run_id: uuid.UUID, trace_id: str | None) -> None:
        if not trace_id:
            return
        async with self.database.session_factory() as session:
            run = await session.get(AgentRun, run_id)
            if run is not None:
                run.langfuse_trace_id = trace_id
                await session.commit()

    async def _copy_artifact(
        self, session: AsyncSession, run: AgentRun, source_path: str | None
    ) -> Artifact | None:
        if not source_path:
            return None
        source = Path(source_path).resolve()
        if not source.is_file() or source.suffix.lower() != ".png":
            return None
        artifact_id = uuid.uuid4()
        destination = (self.settings.artifact_dir / f"{artifact_id}.png").resolve()
        await asyncio.to_thread(shutil.copy2, source, destination)
        artifact = Artifact(
            id=artifact_id,
            owner_user_id=run.owner_user_id,
            run_id=run.id,
            mime_type="image/png",
            storage_path=str(destination),
        )
        session.add(artifact)
        return artifact

    async def _complete(self, turn: PreparedTurn, state: dict[str, Any], answer: str) -> None:
        async with self.database.session_factory() as session:
            run = await session.get(AgentRun, turn.run_id)
            message = await session.get(Message, turn.assistant_message_id)
            conversation = await session.get(Conversation, turn.conversation_id)
            assert run is not None and message is not None and conversation is not None
            rows = jsonable_encoder(state.get("rows") or [])
            row_count = len(rows)
            preview = rows[: self.settings.result_preview_rows]
            run.status = RunStatus.COMPLETED
            run.answer = answer
            run.validated_sql = state.get("validated_sql") or state.get("sql")
            run.selected_tables = list(state.get("selected_tables") or [])
            run.columns = list(state.get("columns") or [])
            run.rows = preview
            run.row_count = row_count
            run.truncated = row_count > len(preview)
            run.retry_count = int(state.get("retry_count") or 0)
            run.completed_at = utcnow()
            message.content = answer
            message.status = MessageStatus.COMPLETED
            message.completed_at = run.completed_at
            conversation.last_message_at = run.completed_at
            conversation.updated_at = run.completed_at
            await self._copy_artifact(session, run, state.get("chart_path"))
            await session.commit()

    async def _fail(
        self,
        turn: PreparedTurn,
        *,
        code: str,
        detail: str,
        cancelled: bool = False,
    ) -> None:
        async with self.database.session_factory() as session:
            run = await session.get(AgentRun, turn.run_id)
            message = await session.get(Message, turn.assistant_message_id)
            if run is None or message is None:
                return
            now = utcnow()
            run.status = RunStatus.CANCELLED if cancelled else RunStatus.FAILED
            run.error_code = code
            run.error_detail = detail[:500]
            run.completed_at = now
            message.status = MessageStatus.CANCELLED if cancelled else MessageStatus.FAILED
            message.content = "" if cancelled else "The analysis could not be completed."
            message.completed_at = now
            await session.commit()

    async def stream_turn(self, turn: PreparedTurn) -> AsyncIterator[AgentEvent]:
        if turn.replay:
            yield AgentEvent("result", {"replay": True})
            return
        answer_parts: list[str] = []
        state: dict[str, Any] | None = None
        try:
            await self._set_running(turn.run_id)
            history = history_messages(await self._load_history(turn))
            with self.observability.chat_trace(
                user_id=str(turn.user_id),
                conversation_id=str(turn.conversation_id),
                request_id=turn.request_id,
                run_id=str(turn.run_id),
                question=turn.question,
            ) as trace:
                await self._set_trace_id(turn.run_id, trace.trace_id)
                async with asyncio.timeout(self.settings.agent_timeout_seconds):
                    async for event in self.runner.stream(
                        question=turn.question,
                        history=history,
                        conversation_id=str(turn.conversation_id),
                        run_id=str(turn.run_id),
                        callbacks=trace.callbacks,
                        metadata={
                            "request_id": turn.request_id,
                            "user_id": str(turn.user_id),
                            "conversation_id": str(turn.conversation_id),
                        },
                    ):
                        if await self._is_cancelled(turn.run_id):
                            raise TurnCancelled
                        if event.kind == "token":
                            answer_parts.append(str(event.data.get("text", "")))
                        elif event.kind == "result":
                            state = event.data
                        yield event
            if state is None:
                raise RuntimeError("Agent returned no terminal state")
            if await self._is_cancelled(turn.run_id):
                raise TurnCancelled
            answer = "".join(answer_parts) or str(state.get("answer") or "")
            await self._complete(turn, state, answer)
        except TurnCancelled:
            await self._fail(
                turn,
                code="run_cancelled",
                detail="The run was cancelled.",
                cancelled=True,
            )
            yield AgentEvent("result", {"cancelled": True})
        except TimeoutError:
            await self._fail(turn, code="agent_timeout", detail="The analysis timed out.")
            raise ApiError(504, "agent_timeout", "The analysis exceeded its time limit.") from None
        except ApiError:
            raise
        except Exception as exc:
            await self._fail(
                turn,
                code="agent_failed",
                detail=f"Agent failed with {type(exc).__name__}.",
            )
            raise ApiError(500, "agent_failed", "The analysis could not be completed.") from exc

    async def response(self, turn: PreparedTurn) -> ChatResponse:
        async with self.database.session_factory() as session:
            user_message = await session.get(Message, turn.user_message_id)
            assistant_message = await session.get(Message, turn.assistant_message_id)
            if user_message is None or assistant_message is None:
                raise ApiError(404, "run_not_found", "Run not found.", title="Not found")
            return ChatResponse(
                user_message=await message_response(
                    session, user_message, self.settings.api_v1_prefix
                ),
                assistant_message=await message_response(
                    session, assistant_message, self.settings.api_v1_prefix
                ),
            )

    async def run_non_streaming(self, turn: PreparedTurn) -> ChatResponse:
        if not turn.replay:
            async for _ in self.stream_turn(turn):
                pass
        return await self.response(turn)

    async def cancel(self, run_id: uuid.UUID, user_id: uuid.UUID) -> None:
        async with self.database.session_factory() as session:
            run = await session.scalar(
                select(AgentRun).where(AgentRun.id == run_id, AgentRun.owner_user_id == user_id)
            )
            if run is None:
                raise ApiError(404, "run_not_found", "Run not found.", title="Not found")
            if run.status not in {RunStatus.QUEUED, RunStatus.RUNNING}:
                raise ApiError(409, "run_not_active", "Only an active run can be cancelled.")
            run.status = RunStatus.CANCELLED
            run.error_code = "run_cancelled"
            run.completed_at = utcnow()
            message = await session.get(Message, run.assistant_message_id)
            if message is not None:
                message.status = MessageStatus.CANCELLED
                message.completed_at = run.completed_at
            await session.commit()
