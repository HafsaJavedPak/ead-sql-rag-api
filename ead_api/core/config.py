from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "ead-sql-rag-api"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    docs_enabled: bool = True
    allowed_hosts: str = "localhost,127.0.0.1,testserver"
    cors_origins: str = "http://localhost:3000"

    app_database_url: str = "postgresql+asyncpg://ead_app:change-me@localhost:5432/ead_app"
    langgraph_database_url: str = ""
    database_echo: bool = False
    auto_create_schema: bool = False

    jwt_secret_key: str = "development-only-change-this-secret-before-production"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "ead-sql-rag-api"
    jwt_audience: str = "ead-sql-rag-client"
    access_token_ttl_minutes: int = Field(default=15, ge=5, le=60)
    refresh_token_ttl_days: int = Field(default=30, ge=1, le=90)

    llm_provider: str = "groq"
    llm_model: str = "openai/gpt-oss-120b"
    groq_api_key: str = ""
    local_base_url: str = "http://localhost:8001/v1"
    local_api_key: str = "not-needed"
    llm_temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    llm_timeout_seconds: int = Field(default=60, ge=5, le=300)
    llm_max_retries: int = Field(default=2, ge=0, le=6)

    embed_provider: str = "huggingface"
    embed_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    langfuse_enabled: bool = False
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_base_url: str = "http://localhost:3000"
    langfuse_tracing_environment: str = "development"
    langfuse_sample_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    langfuse_capture_content: bool = False

    artifact_dir: Path = Path("artifacts")
    max_message_chars: int = Field(default=8000, ge=100, le=50000)
    history_max_messages: int = Field(default=20, ge=2, le=100)
    history_max_tokens: int = Field(default=6000, ge=500, le=50000)
    agent_timeout_seconds: int = Field(default=120, ge=10, le=600)
    result_preview_rows: int = Field(default=100, ge=1, le=500)

    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, value: str) -> str:
        normalized = value.strip().lower().replace("_", "-")
        if normalized not in {"groq", "openai-compatible", "local"}:
            raise ValueError("LLM_PROVIDER must be groq or openai-compatible")
        return "openai-compatible" if normalized == "local" else normalized

    @field_validator("embed_provider")
    @classmethod
    def validate_embed_provider(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"huggingface", "openai-compatible", "lexical"}:
            raise ValueError("EMBED_PROVIDER must be huggingface, openai-compatible, or lexical")
        return normalized

    @model_validator(mode="after")
    def validate_production(self) -> Settings:
        if self.app_env.lower() == "production":
            if self.jwt_secret_key.startswith("development-only") or len(self.jwt_secret_key) < 48:
                raise ValueError(
                    "Production JWT_SECRET_KEY must contain at least 48 random characters"
                )
            if "*" in self.allowed_host_list or "*" in self.cors_origin_list:
                raise ValueError("Production hosts and CORS origins must be explicit")
            if not self.app_database_url.startswith("postgresql+asyncpg://"):
                raise ValueError("Production APP_DATABASE_URL must use PostgreSQL with asyncpg")
            if self.auto_create_schema:
                raise ValueError("AUTO_CREATE_SCHEMA is test-only; use Alembic in production")
            if self.docs_enabled:
                raise ValueError("DOCS_ENABLED must be false in production")
            if not self.langfuse_enabled:
                raise ValueError("LANGFUSE_ENABLED must be true in production")
        if (
            self.app_env.lower() == "production"
            and self.llm_provider == "groq"
            and not self.groq_api_key
        ):
            raise ValueError("GROQ_API_KEY is required when LLM_PROVIDER=groq")
        if self.app_env.lower() == "production" and not self.langgraph_database_url:
            raise ValueError("Production LANGGRAPH_DATABASE_URL is required for durable memory")
        if self.langfuse_enabled and not (self.langfuse_public_key and self.langfuse_secret_key):
            raise ValueError("Langfuse keys are required when LANGFUSE_ENABLED=true")
        return self

    @property
    def allowed_host_list(self) -> list[str]:
        return [item.strip() for item in self.allowed_hosts.split(",") if item.strip()]

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
