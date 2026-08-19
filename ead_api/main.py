from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from ead_agent.graph import build_graph
from ead_api.agent.runner import SqlAgentRunner
from ead_api.api.routers import auth, conversations, health, messages, runs, users
from ead_api.core.config import Settings, get_settings
from ead_api.core.observability import Observability
from ead_api.db.base import Base, Database
from ead_api.errors import install_error_handlers
from ead_api.middleware.request_id import RequestIdMiddleware
from ead_api.services.chat import ChatService


def create_app(settings: Settings | None = None) -> FastAPI:
    configured = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        database = Database(configured.app_database_url, echo=configured.database_echo)
        app.state.database = database
        configured.artifact_dir.mkdir(parents=True, exist_ok=True)
        if configured.auto_create_schema:
            async with database.engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)

        observability = Observability(configured)
        app.state.observability = observability
        async with AsyncExitStack() as stack:
            checkpointer: Any
            if configured.langgraph_database_url:
                from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

                checkpoint_context = AsyncPostgresSaver.from_conn_string(
                    configured.langgraph_database_url
                )
                checkpointer = await stack.enter_async_context(checkpoint_context)
                await checkpointer.setup()
            else:
                from langgraph.checkpoint.memory import InMemorySaver

                checkpointer = InMemorySaver()

            graph = build_graph(checkpointer=checkpointer, include_summary=False)
            runner = SqlAgentRunner(
                graph,
                history_max_messages=configured.history_max_messages,
                history_max_tokens=configured.history_max_tokens,
            )
            app.state.chat_service = ChatService(
                database,
                runner,
                observability,
                configured,
            )
            try:
                yield
            finally:
                observability.shutdown()
                await database.dispose()

    app = FastAPI(
        title="EAD SQL RAG API",
        version="1.0.0",
        description="Authenticated multi-user SQL RAG chat API with streaming and charts.",
        docs_url="/docs" if configured.docs_enabled else None,
        redoc_url="/redoc" if configured.docs_enabled else None,
        openapi_url="/openapi.json" if configured.docs_enabled else None,
        lifespan=lifespan,
    )
    app.state.settings = configured
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=configured.allowed_host_list)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=configured.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )
    install_error_handlers(app)
    app.include_router(health.router)
    app.include_router(auth.router, prefix=configured.api_v1_prefix)
    app.include_router(users.router, prefix=configured.api_v1_prefix)
    app.include_router(conversations.router, prefix=configured.api_v1_prefix)
    app.include_router(messages.conversation_router, prefix=configured.api_v1_prefix)
    app.include_router(messages.message_router, prefix=configured.api_v1_prefix)
    app.include_router(runs.run_router, prefix=configured.api_v1_prefix)
    app.include_router(runs.artifact_router, prefix=configured.api_v1_prefix)
    return app


app = create_app()
