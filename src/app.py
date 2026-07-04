"""Flask app: / chat UI, /chat JSON API, /health, optional auto-index on /chat if empty Chroma."""

from __future__ import annotations

import logging
import os
import traceback
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request

from src.rag import RAGEngine

log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def ensure_indexed(rag: RAGEngine) -> bool:
    try:
        if rag.collection.count() > 0:
            return True
    except Exception:  # noqa: BLE001
        log.debug("Chroma not ready: %s", traceback.format_exc())
    try:
        from src import ingest

        return ingest.ingest(force=False) > 0
    except Exception:  # noqa: BLE001
        log.error("Ingestion failed: %s", traceback.format_exc())
    return False


def create_app(rag: RAGEngine | None = None) -> Flask:
    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "templates"),
    )
    engine: RAGEngine = rag or RAGEngine()

    @app.route("/")
    def home() -> str:
        return render_template("index.html")

    @app.get("/health")
    def health() -> Any:
        try:
            n = int(engine.collection.count())
        except Exception:  # noqa: BLE001
            n = 0
        return jsonify(
            {
                "status": "ok",
                "indexed_chunks": n,
            }
        )

    @app.post("/chat")
    def chat() -> Any:
        if not request.is_json:
            return jsonify({"error": "Expected application/json"}), 400
        data = request.get_json(silent=True) or {}
        q = (data.get("question") or "").strip()
        if not q:
            return jsonify({"error": "Missing question"}), 400
        if not ensure_indexed(engine):
            return (
                jsonify(
                    {
                        "error": (
                            "Index is empty. Set RAG_CORPUS_DIR to your corpus root "
                            "(e.g. .../rag_policy_corpus) and run: python -m scripts.ingest"
                        ),
                    }
                ),
                503,
            )
        return jsonify(engine.answer(q))

    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    app = create_app()
    app.run(
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true", "yes"),
    )


if __name__ == "__main__":
    main()
