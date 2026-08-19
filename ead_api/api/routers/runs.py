from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ead_api.core.config import Settings
from ead_api.dependencies import (
    get_chat_service,
    get_current_user,
    get_session,
    get_settings_from_app,
)
from ead_api.errors import ApiError
from ead_api.models import AgentRun, Artifact, User
from ead_api.schemas import RunResponse
from ead_api.services.chat import ChatService
from ead_api.services.messages import run_response

run_router = APIRouter(prefix="/runs", tags=["runs"])
artifact_router = APIRouter(prefix="/artifacts", tags=["artifacts"])


@run_router.get("/{run_id}", response_model=RunResponse)
async def get_run(
    run_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings_from_app),
) -> RunResponse:
    run = await session.scalar(
        select(AgentRun).where(AgentRun.id == run_id, AgentRun.owner_user_id == user.id)
    )
    if run is None:
        raise ApiError(404, "run_not_found", "Run not found.", title="Not found")
    return await run_response(session, run, settings.api_v1_prefix)


@run_router.post("/{run_id}/cancel", status_code=status.HTTP_202_ACCEPTED)
async def cancel_run(
    run_id: uuid.UUID,
    user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> dict[str, str]:
    await chat_service.cancel(run_id, user.id)
    return {"status": "cancellation_requested", "run_id": str(run_id)}


@artifact_router.get("/{artifact_id}", response_class=FileResponse)
async def get_artifact(
    artifact_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> FileResponse:
    artifact = await session.scalar(
        select(Artifact).where(
            Artifact.id == artifact_id,
            Artifact.owner_user_id == user.id,
        )
    )
    if artifact is None:
        raise ApiError(404, "artifact_not_found", "Artifact not found.", title="Not found")
    path = Path(artifact.storage_path)
    if not path.is_file():
        raise ApiError(404, "artifact_not_found", "Artifact not found.", title="Not found")
    return FileResponse(path, media_type=artifact.mime_type, filename=path.name)
