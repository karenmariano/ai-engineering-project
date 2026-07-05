"""Configuration: corpus path, retrieval, and OpenAI-compatible LLM."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load from project root so keys work when cwd is not the repo (e.g. `python -m src.app` from elsewhere)
_env_file = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_file)

SEED: int = int(os.environ.get("RAG_SEED", "42"))


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_corpus_dir() -> Path:
    """Root folder that contains `chunks/chunks.jsonl` (RAG-optimized pack)."""
    env = (os.environ.get("RAG_CORPUS_DIR") or "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if not p.is_dir():
            raise FileNotFoundError(
                f"RAG_CORPUS_DIR is not a directory: {p}. "
                "Set it to your policy corpus root (e.g. .../rag_policy_corpus)."
            )
        return p
    # Optional: place a symlink at data/corpus -> your corpus
    fallback = project_root() / "data" / "corpus"
    if fallback.is_dir():
        return fallback.resolve()
    return fallback


def chunks_jsonl_path() -> Path:
    return get_corpus_dir() / "chunks" / "chunks.jsonl"


def get_chroma_dir() -> Path:
    d = project_root() / "data" / "chroma"
    d.mkdir(parents=True, exist_ok=True)
    return d


# Retrieval
RAG_TOP_K: int = int(os.environ.get("RAG_TOP_K", "8"))
# Distance gate used by vector backends; lexical retrieval returns distance 0.
RAG_MAX_L2_DISTANCE: float = float(os.environ.get("RAG_MAX_L2_DISTANCE", "1.15"))

# Generation: enough room for full policy sections (e.g. PTO rules, approval steps)
RAG_MAX_ANSWER_CHARS: int = int(os.environ.get("RAG_MAX_ANSWER_CHARS", "12000"))
# LLM output budget (tokens); higher = more complete answers from the model
LLM_MAX_TOKENS: int = int(os.environ.get("LLM_MAX_TOKENS", "2000"))
LLM_TIMEOUT_SECONDS: float = float(os.environ.get("LLM_TIMEOUT_SECONDS", "20"))
# Extractive path: max chars from the best-matching chunk (sections are pre-chunked; avoid truncating mid-policy)
EXTRACTIVE_MAX_CHARS: int = int(os.environ.get("EXTRACTIVE_MAX_CHARS", "10000"))
# JSON citation snippets in /chat (evidence text per chunk in the response)
CITATION_SNIPPET_MAX_CHARS: int = int(os.environ.get("CITATION_SNIPPET_MAX_CHARS", "2000"))


def llm_api_key() -> str:
    return (os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY") or "").strip()


def require_llm() -> bool:
    return os.environ.get("REQUIRE_LLM", "true").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    )


def openai_base_url() -> str:
    return (os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")


def llm_model() -> str:
    """OpenRouter model ids look like `google/gemma-2-9b-it:free`, not `openrouter/free`."""
    m = (os.environ.get("LLM_MODEL") or "gpt-4o-mini").strip()
    if m.lower() in ("openrouter/free", "openrouter.free"):
        raise ValueError(
            "LLM_MODEL cannot be 'openrouter/free' — that is not a valid OpenRouter model. "
            "Pick a model from https://openrouter.ai/models (e.g. google/gemma-2-9b-it:free)."
        )
    return m


def embedding_model() -> str:
    return (os.environ.get("EMBEDDING_MODEL") or "lexical").strip()


def retriever_backend() -> str:
    return os.environ.get("RETRIEVER_BACKEND", embedding_model()).strip().lower()
