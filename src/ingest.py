"""Load pre-chunked policy JSONL into Chroma (matches rag_policy_corpus `chunks/chunks.jsonl`)."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

from src.config import embedding_model, get_chroma_dir, get_corpus_dir

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
    persist = str(get_chroma_dir())
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=embedding_model()
    )
    client = chromadb.PersistentClient(path=persist)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "l2"},
    )


def ingest(corpus_dir: Path | None = None, force: bool = False) -> int:
    root = (corpus_dir or get_corpus_dir()).resolve()
    path = root / "chunks" / "chunks.jsonl"
    rows = load_chunks_jsonl(path)
    if not rows:
        raise ValueError(f"No rows in {path}")

    client = chromadb.PersistentClient(path=str(get_chroma_dir()))
    if force:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:  # noqa: BLE001
            pass

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=embedding_model()
    )
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "l2"},
    )
    if not force and collection.count() > 0:
        log.info("Chroma has %s chunks; skip (use --force to rebuild).", collection.count())
        return collection.count()

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, str]] = []
    for r in rows:
        cid = str(r["chunk_id"])
        text = str(r.get("text") or "")
        ids.append(cid)
        documents.append(text)
        metadatas.append(
            {
                "chunk_id": cid,
                "doc_slug": str(r.get("doc_slug") or ""),
                "doc_title": str(r.get("doc_title") or ""),
                "section_heading": str(r.get("section_heading") or ""),
                "owner": str(r.get("owner") or ""),
            }
        )
    batch = 100
    for i in range(0, len(ids), batch):
        collection.add(
            ids=ids[i : i + batch],
            documents=documents[i : i + batch],
            metadatas=metadatas[i : i + batch],
        )
    log.info("Indexed %s chunks from %s", len(ids), path)
    return len(ids)
