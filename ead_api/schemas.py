from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from ead_api.models import ConversationStatus, MessageRole, MessageStatus, RunStatus


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RegisterRequest(ApiModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=256)
    display_name: str | None = Field(default=None, min_length=1, max_length=120)


class LoginRequest(ApiModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)


class RefreshRequest(ApiModel):
    refresh_token: str = Field(min_length=32, max_length=512)


class TokenPair(ApiModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class UserResponse(ApiModel):
    id: uuid.UUID
    email: EmailStr
    display_name: str | None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime


class RegisterResponse(ApiModel):
    user: UserResponse
    tokens: TokenPair


class UserPatch(ApiModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)


class ConversationCreate(ApiModel):
    title: str = Field(default="New conversation", min_length=1, max_length=240)


class ConversationPatch(ApiModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    status: ConversationStatus | None = None


class ConversationResponse(ApiModel):
    id: uuid.UUID
    title: str
    status: ConversationStatus
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime | None
    message_count: int = 0


class ConversationPage(ApiModel):
    items: list[ConversationResponse]
    next_cursor: str | None = None


class ChatRequest(ApiModel):
    content: str = Field(min_length=1)

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Message content cannot be blank")
        return stripped


class ArtifactResponse(ApiModel):
    id: uuid.UUID
    kind: str
    mime_type: str
    url: str


class RunResponse(ApiModel):
    id: uuid.UUID
    status: RunStatus
    answer: str | None
    validated_sql: str | None
    selected_tables: list[str] | None
    columns: list[str] | None
    rows: list[list[Any]] | None
    row_count: int
    truncated: bool
    retry_count: int
    error_code: str | None
    error_detail: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    artifacts: list[ArtifactResponse] = Field(default_factory=list)


class MessageResponse(ApiModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sequence_no: int
    role: MessageRole
    status: MessageStatus
    content: str
    created_at: datetime
    completed_at: datetime | None
    run: RunResponse | None = None


class MessagePage(ApiModel):
    items: list[MessageResponse]
    next_cursor: str | None = None


class ChatResponse(ApiModel):
    user_message: MessageResponse
    assistant_message: MessageResponse


class HealthResponse(ApiModel):
    status: Literal["ok", "degraded"]
    checks: dict[str, bool] = Field(default_factory=dict)
