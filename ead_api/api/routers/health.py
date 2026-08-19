from __future__ import annotations

from fastapi import APIRouter, Depends

from ead_api.db.base import Database
from ead_api.dependencies import get_database
from ead_api.errors import ApiError
from ead_api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health/live", response_model=HealthResponse)
async def live() -> HealthResponse:
    return HealthResponse(status="ok", checks={"process": True})


@router.get("/health/ready", response_model=HealthResponse)
async def ready(database: Database = Depends(get_database)) -> HealthResponse:
    try:
        database_ok = await database.ping()
    except Exception as exc:
        raise ApiError(
            503,
            "dependency_unavailable",
            "The application database is unavailable.",
            title="Service unavailable",
        ) from exc
    return HealthResponse(status="ok", checks={"application_database": database_ok})
