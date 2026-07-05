from __future__ import annotations

import json

import pytest
from unittest.mock import MagicMock

from src.app import create_app


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("REQUIRE_LLM", "false")
    rag = MagicMock()
    rag.collection.count.return_value = 1
    rag.answer.return_value = {
        "answer": "ok",
        "citations": [
            {
                "chunk_id": "x::1",
                "doc_title": "T",
                "section_heading": "S",
                "doc_slug": "x",
                "snippet": "s",
            }
        ],
        "snippets": ["s"],
        "latency_ms": 1.0,
        "refused": False,
    }
    app = create_app(rag=rag)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_health(client) -> None:
    res = client.get("/health")
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "ok"


def test_chat(client) -> None:
    res = client.post(
        "/chat",
        data=json.dumps({"question": "What is PTO?"}),
        content_type="application/json",
    )
    assert res.status_code == 200
    body = res.get_json()
    assert body.get("answer") == "ok"
