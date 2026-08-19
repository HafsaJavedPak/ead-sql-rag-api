"""LangChain model and embedding adapters for Groq and local inference."""

from __future__ import annotations

import json
import re
from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from ead_agent.config import settings


@lru_cache(maxsize=1)
def get_chat_model():
    provider = settings.llm_provider
    if provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=settings.llm_model,
            api_key=settings.groq_api_key,
            temperature=0,
            timeout=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
        )

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=settings.llm_model,
        base_url=settings.local_base_url,
        api_key=settings.local_api_key,
        temperature=0,
        timeout=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )


def _text(message: AIMessage) -> str:
    if isinstance(message.content, str):
        return message.content.strip()
    parts: list[str] = []
    for block in message.content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(str(block.get("text", "")))
    return "".join(parts).strip()


def _config(
    config: RunnableConfig | None,
    *,
    run_name: str,
    tags: list[str] | None = None,
) -> RunnableConfig:
    merged: RunnableConfig = dict(config or {})
    merged["run_name"] = run_name
    if tags:
        merged["tags"] = list(dict.fromkeys([*(merged.get("tags") or []), *tags]))
    return merged


def chat(
    system: str,
    user: str,
    temperature: float = 0.0,
    max_tokens: int = 1200,
    *,
    config: RunnableConfig | None = None,
    run_name: str = "llm.chat",
    tags: list[str] | None = None,
) -> str:
    model = get_chat_model().bind(temperature=temperature, max_tokens=max_tokens)
    response = model.invoke(
        [SystemMessage(content=system), HumanMessage(content=user)],
        config=_config(config, run_name=run_name, tags=tags),
    )
    return _text(response)


async def achat(
    system: str,
    user: str,
    temperature: float = 0.0,
    max_tokens: int = 1200,
    *,
    config: RunnableConfig | None = None,
    run_name: str = "llm.chat",
    tags: list[str] | None = None,
) -> str:
    model = get_chat_model().bind(temperature=temperature, max_tokens=max_tokens)
    response = await model.ainvoke(
        [SystemMessage(content=system), HumanMessage(content=user)],
        config=_config(config, run_name=run_name, tags=tags),
    )
    return _text(response)


async def astream_chat(
    system: str,
    user: str,
    temperature: float = 0.0,
    max_tokens: int = 1200,
    *,
    config: RunnableConfig | None = None,
    run_name: str = "llm.chat",
    tags: list[str] | None = None,
) -> AsyncIterator[str]:
    model = get_chat_model().bind(temperature=temperature, max_tokens=max_tokens)
    async for chunk in model.astream(
        [SystemMessage(content=system), HumanMessage(content=user)],
        config=_config(config, run_name=run_name, tags=tags),
    ):
        text = chunk.text
        if text:
            yield text


def chat_json(
    system: str,
    user: str,
    temperature: float = 0.0,
    *,
    config: RunnableConfig | None = None,
    run_name: str = "llm.json",
) -> dict[str, Any]:
    raw = chat(
        system + "\n\nRespond with a single JSON object and nothing else.",
        user,
        temperature=temperature,
        config=config,
        run_name=run_name,
    )
    return _parse_json(raw)


def _parse_json(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        value = json.loads(raw)
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.S)
        if match:
            try:
                value = json.loads(match.group(0))
                return value if isinstance(value, dict) else {}
            except json.JSONDecodeError:
                pass
    return {}


@lru_cache(maxsize=1)
def get_embeddings():
    if settings.embed_provider == "huggingface":
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(model_name=settings.embed_model)

    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(
        model=settings.embed_model,
        base_url=settings.local_base_url,
        api_key=settings.local_api_key,
    )


def embed_documents(texts: list[str]) -> list[list[float]]:
    return get_embeddings().embed_documents(texts)


def embed_query(text: str) -> list[float]:
    return get_embeddings().embed_query(text)
