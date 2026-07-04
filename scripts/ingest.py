"""CLI: index corpus into Chroma. Requires RAG_CORPUS_DIR or data/corpus symlink."""

from __future__ import annotations

import argparse
import logging
import pathlib
import sys

# `python scripts/ingest.py` does not put the repo root on sys.path; `python -m scripts.ingest` does.
_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.config import get_corpus_dir
from src import ingest as ingest_mod

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Index chunks/chunks.jsonl into Chroma")
    p.add_argument(
        "--corpus",
        type=str,
        default=None,
        help="Override corpus root (default: RAG_CORPUS_DIR or data/corpus)",
    )
    p.add_argument("--force", action="store_true", help="Rebuild the vector index from scratch")
    args = p.parse_args()
    root = pathlib.Path(args.corpus).resolve() if args.corpus else get_corpus_dir()
    n = ingest_mod.ingest(corpus_dir=root, force=args.force)
    print(f"Indexed {n} chunks from {root / 'chunks' / 'chunks.jsonl'}")
