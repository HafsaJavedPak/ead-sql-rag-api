"""Central config. Everything comes from .env -- nothing is hardcoded.

Import `settings` from here; do not read os.environ elsewhere.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# config.py lives in ead_agent/, so the project root is one level up.
# .env stays at the project root; generated caches go in .cache/ there.
PKG_DIR = Path(__file__).resolve().parent
ROOT = PKG_DIR.parent
CACHE_DIR = ROOT / ".cache"
load_dotenv(ROOT / ".env")


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    # --- LLM ---
    llm_provider: str = os.getenv("LLM_PROVIDER", "groq").strip().lower().replace("_", "-")
    llm_model: str = os.getenv("LLM_MODEL", "openai/gpt-oss-120b").strip()
    groq_api_key: str = os.getenv("GROQ_API_KEY", "").strip()
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "").strip()
    local_base_url: str = os.getenv("LOCAL_BASE_URL", "http://localhost:8001/v1").strip()
    local_api_key: str = os.getenv("LOCAL_API_KEY", "not-needed").strip()
    llm_timeout_seconds: int = _int("LLM_TIMEOUT_SECONDS", 60)
    llm_max_retries: int = _int("LLM_MAX_RETRIES", 2)

    # --- Embeddings ---
    embed_provider: str = os.getenv("EMBED_PROVIDER", "huggingface").strip().lower()
    embed_model: str = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2").strip()
    local_embed_model: str = os.getenv(
        "LOCAL_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    ).strip()

    # --- Database ---
    db_host: str = os.getenv("DB_HOST", "127.0.0.1").strip()
    db_port: int = _int("DB_PORT", 3306)
    db_name: str = os.getenv("DB_NAME", "ead_db").strip()
    db_user: str = os.getenv("DB_USER", "root").strip()
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_readonly_user: str = os.getenv("DB_READONLY_USER", "ead_ro").strip()
    db_readonly_password: str = os.getenv("DB_READONLY_PASSWORD", "")
    analytics_database_url: str = os.getenv("ANALYTICS_DATABASE_URL", "").strip()
    # PEM certificate content (not a path) for managed hosts that enforce TLS,
    # e.g. Aiven. Empty disables SSL, for local/Compose MySQL that doesn't
    # need it.
    db_ssl_ca: str = os.getenv("DB_SSL_CA", "").strip()

    # --- Guard rails ---
    max_retries: int = _int("MAX_RETRIES", 3)
    row_limit: int = _int("ROW_LIMIT", 500)
    query_timeout_seconds: int = _int("QUERY_TIMEOUT_SECONDS", 30)
    top_k_tables: int = _int("TOP_K_TABLES", 25)

    # --- Paths ---
    catalog_path: Path = CACHE_DIR / "schema_catalog.json"
    embeddings_path: Path = CACHE_DIR / "embeddings_cache.npz"
    charts_dir: Path = ROOT / "charts_out"

    def validate(self) -> list[str]:
        """Return a list of human-readable problems (empty == good to go)."""
        problems = []
        if self.llm_provider == "groq" and not self.groq_api_key:
            problems.append("LLM_PROVIDER=groq but GROQ_API_KEY is empty.")
        if self.llm_provider not in {"groq", "openai-compatible", "local"}:
            problems.append(
                f"LLM_PROVIDER must be 'groq' or 'openai-compatible', got {self.llm_provider!r}."
            )
        if self.embed_provider not in {"huggingface", "openai-compatible", "lexical"}:
            problems.append(
                "EMBED_PROVIDER must be 'huggingface', 'openai-compatible', or 'lexical', "
                f"got {self.embed_provider!r}."
            )
        if not self.analytics_database_url and not self.db_readonly_password:
            problems.append(
                "DB_READONLY_PASSWORD is empty -- generated SQL has no safe user to run as."
            )
        return problems


settings = Settings()
