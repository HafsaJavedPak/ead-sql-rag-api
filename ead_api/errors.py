from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


@dataclass
class ApiError(Exception):
    status_code: int
    code: str
    detail: str
    title: str = "Request failed"
    headers: dict[str, str] | None = None


def problem(
    request: Request, *, status: int, code: str, title: str, detail: str
) -> dict[str, object]:
    return {
        "type": f"https://ead.local/problems/{code}",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.url.path,
        "code": code,
        "request_id": getattr(request.state, "request_id", None),
    }


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            problem(
                request,
                status=exc.status_code,
                code=exc.code,
                title=exc.title,
                detail=exc.detail,
            ),
            status_code=exc.status_code,
            headers=exc.headers,
            media_type="application/problem+json",
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            {
                **problem(
                    request,
                    status=422,
                    code="validation_error",
                    title="Validation error",
                    detail="The request did not match the API contract.",
                ),
                "errors": exc.errors(),
            },
            status_code=422,
            media_type="application/problem+json",
        )
