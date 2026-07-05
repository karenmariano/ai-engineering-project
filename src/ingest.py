"""Validate or index pre-chunked policy JSONL (`chunks/chunks.jsonl`)."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from src.config import get_corpus_dir

log = logging.getLogger(__name__)

COLLECTION_NAME = "policy_chunks"


def load_chunks_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing {path}. Set RAG_CORPUS_DIR to the corpus root that contains "
            "chunks/chunks.jsonl (e.g. .../rag_policy_corpus), or symlink it to data/corpus."
        )
    out: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def get_collection() -> Any:
    from src.lexical import LexicalRetriever

    return LexicalRetriever()


def ingest(corpus_dir: Path | None = None, force: bool = False) -> int:
    root = (corpus_dir or get_corpus_dir()).resolve()
    path = root / "chunks" / "chunks.jsonl"
    rows = load_chunks_jsonl(path)
    if not rows:
        raise ValueError(f"No rows in {path}")
    log.info("Validated %s lexical chunks from %s", len(rows), path)
    return len(rows)
