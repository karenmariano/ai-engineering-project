"""Flask app: / chat UI, /chat JSON API, /health."""

from __future__ import annotations

import logging
import os
import traceback
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request
from openai import OpenAI

from src.config import LLM_TIMEOUT_SECONDS, llm_api_key, llm_model, openai_base_url, require_llm
from src.rag import RAGEngine

log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def ensure_indexed(rag: RAGEngine) -> bool:
    try:
        if rag.collection.count() > 0:
            return True
    except Exception:  # noqa: BLE001
        log.debug("Retriever not ready: %s", traceback.format_exc())
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
                "llm_required": require_llm(),
                "llm_configured": bool(llm_api_key()),
                "llm_model": llm_model() if llm_api_key() else None,
                "llm_base_url": openai_base_url() if llm_api_key() else None,
            }
        )

    @app.get("/llm-check")
    def llm_check() -> Any:
        key = llm_api_key()
        base_url = openai_base_url()
        if not key:
            return (
                jsonify(
                    {
                        "ok": False,
                        "error": "LLM_API_KEY or OPENAI_API_KEY is not configured.",
                        "llm_required": require_llm(),
                        "llm_configured": False,
                        "llm_base_url": base_url,
                    }
                ),
                503,
            )
        model = llm_model()
        try:
            client = OpenAI(
                api_key=key,
                base_url=base_url,
                timeout=LLM_TIMEOUT_SECONDS,
                max_retries=0,
            )
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Reply with OK only."}],
                max_tokens=8,
                temperature=0,
            )
            return jsonify(
                {
                    "ok": True,
                    "llm_configured": True,
                    "llm_base_url": base_url,
                    "llm_model": model,
                    "response": (resp.choices[0].message.content or "").strip(),
                }
            )
        except Exception as exc:  # noqa: BLE001
            log.exception("LLM diagnostic check failed")
            return (
                jsonify(
                    {
                        "ok": False,
                        "llm_configured": True,
                        "llm_base_url": base_url,
                        "llm_model": model,
                        "error_type": type(exc).__name__,
                        "error": str(exc)[:1000],
                    }
                ),
                502,
            )

    @app.post("/chat")
    def chat() -> Any:
        if not request.is_json:
            return jsonify({"error": "Expected application/json"}), 400
        data = request.get_json(silent=True) or {}
        q = (data.get("question") or "").strip()
        if not q:
            return jsonify({"error": "Missing question"}), 400
        if require_llm() and not llm_api_key():
            return (
                jsonify(
                    {
                        "error": (
                            "LLM_API_KEY is required for chat. Set LLM_API_KEY in Render "
                            "environment variables, plus OPENAI_BASE_URL and LLM_MODEL if "
                            "using a non-OpenAI provider."
                        ),
                        "llm_required": True,
                        "llm_configured": False,
                    }
                ),
                503,
            )
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
