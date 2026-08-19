"""Rank 146 tables against a question so only a handful reach the SQL prompt.

Embeddings are cached to disk and keyed by a hash of the catalog content, so
they recompute only when the schema actually changes -- not on every startup.

Retrieval is hybrid: cosine similarity plus a small lexical bonus for exact
table/column name mentions. Pure embeddings under-rank tables whose meaning
lives in the name ("wq_donors" for "which donors...") while pure keyword
search misses paraphrases ("funding agency" -> donors).
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

import numpy as np

from ead_agent.config import settings
from ead_agent.llm import embed_documents, embed_query
from ead_agent.schema_catalog import load_catalog

# Framework tables can still be selected, but should not outrank domain tables.
FRAMEWORK_PENALTY = 0.15
LEXICAL_BONUS = 0.08


def _catalog_fingerprint(catalog: dict[str, Any]) -> str:
    docs = "|".join(sorted(catalog["tables"]))
    return hashlib.sha256((docs + str(len(catalog["join_graph"]["edges"]))).encode()).hexdigest()[
        :16
    ]


def _table_docs(catalog: dict[str, Any]) -> tuple[list[str], list[str]]:
    names, docs = [], []
    for name in sorted(catalog["tables"]):
        t = catalog["tables"][name]
        cols = ", ".join(c["name"] for c in t["columns"][:24])
        docs.append(f"{name}: {t['description']}. Columns: {cols}")
        names.append(name)
    return names, docs


def _load_or_build_embeddings(catalog: dict[str, Any]) -> tuple[list[str], np.ndarray]:
    names, docs = _table_docs(catalog)
    fp = _catalog_fingerprint(catalog)

    if settings.embeddings_path.exists():
        cached = np.load(settings.embeddings_path, allow_pickle=True)
        if (
            str(cached.get("fingerprint", "")) == fp
            and str(cached.get("provider", ""))
            == f"{settings.embed_provider}:{settings.embed_model}"
        ):
            return list(cached["names"]), cached["vectors"]

    settings.embeddings_path.parent.mkdir(parents=True, exist_ok=True)
    vectors = np.array(embed_documents(docs), dtype=np.float32)
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-9
    np.savez(
        settings.embeddings_path,
        names=np.array(names),
        vectors=vectors,
        fingerprint=fp,
        provider=f"{settings.embed_provider}:{settings.embed_model}",
    )
    return names, vectors


def _lexical_hits(question: str, catalog: dict[str, Any], name: str) -> float:
    """Bonus when the question literally names the table or one of its columns."""
    q = question.lower()
    bonus = 0.0
    stem = re.sub(r"^wq_", "", name).replace("_", " ")
    if stem and stem in q:
        bonus += LEXICAL_BONUS
    for c in catalog["tables"][name]["columns"][:40]:
        cn = c["name"].replace("_", " ")
        if len(cn) > 5 and cn in q:
            bonus += LEXICAL_BONUS / 2
            break
    return bonus


def top_k_tables(question: str, k: int | None = None) -> list[tuple[str, float]]:
    """Return [(table_name, score)] best-first."""
    k = k or settings.top_k_tables
    catalog = load_catalog()
    if settings.embed_provider == "lexical":
        query_tokens = set(re.findall(r"[a-z0-9]+", question.lower()))
        scored = []
        for name, document in zip(*_table_docs(catalog), strict=True):
            document_tokens = set(re.findall(r"[a-z0-9]+", document.lower()))
            overlap = len(query_tokens & document_tokens)
            score = overlap / max(len(query_tokens), 1) + _lexical_hits(question, catalog, name)
            if catalog["tables"][name]["is_framework"]:
                score -= FRAMEWORK_PENALTY
            scored.append((name, score))
        scored.sort(key=lambda item: (-item[1], item[0]))
        return scored[:k]

    names, vectors = _load_or_build_embeddings(catalog)

    qv = np.array(embed_query(question), dtype=np.float32)
    qv /= np.linalg.norm(qv) + 1e-9
    sims = vectors @ qv

    scored: list[tuple[str, float]] = []
    for name, sim in zip(names, sims, strict=True):
        score = float(sim) + _lexical_hits(question, catalog, name)
        if catalog["tables"][name]["is_framework"]:
            score -= FRAMEWORK_PENALTY
        scored.append((name, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
