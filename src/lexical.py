"""Fast lexical retriever over the bundled policy chunks.

Render free-tier workers can time out while downloading/loading embedding
models during the first request. This retriever keeps the RAG path lightweight:
it loads `chunks.jsonl`, scores policy sections with token/phrase overlap, and
returns retrieval results for the existing RAG engine.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

from src.config import chunks_jsonl_path
from src.ingest import load_chunks_jsonl


TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "before",
    "by",
    "can",
    "do",
    "does",
    "for",
    "from",
    "have",
    "how",
    "in",
    "is",
    "it",
    "must",
    "of",
    "or",
    "our",
    "the",
    "to",
    "what",
    "when",
    "where",
    "who",
    "with",
}


def tokens(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall((text or "").lower()) if t not in STOPWORDS]


@dataclass
class Chunk:
    chunk_id: str
    doc_slug: str
    doc_title: str
    section_heading: str
    owner: str
    text: str
    body_tokens: Counter[str]
    title_tokens: Counter[str]
    heading_tokens: Counter[str]

    @property
    def metadata(self) -> dict[str, str]:
        return {
            "chunk_id": self.chunk_id,
            "doc_slug": self.doc_slug,
            "doc_title": self.doc_title,
            "section_heading": self.section_heading,
            "owner": self.owner,
        }


class LexicalRetriever:
    def __init__(self) -> None:
        rows = load_chunks_jsonl(chunks_jsonl_path())
        self._chunks = [
            Chunk(
                chunk_id=str(r["chunk_id"]),
                doc_slug=str(r.get("doc_slug") or ""),
                doc_title=str(r.get("doc_title") or ""),
                section_heading=str(r.get("section_heading") or ""),
                owner=str(r.get("owner") or ""),
                text=str(r.get("text") or ""),
                body_tokens=Counter(tokens(str(r.get("text") or ""))),
                title_tokens=Counter(tokens(str(r.get("doc_title") or ""))),
                heading_tokens=Counter(tokens(str(r.get("section_heading") or ""))),
            )
            for r in rows
        ]
        doc_freq: Counter[str] = Counter()
        for c in self._chunks:
            doc_freq.update(set(c.body_tokens) | set(c.title_tokens) | set(c.heading_tokens))
        n = max(len(self._chunks), 1)
        self._idf = {term: math.log((n + 1) / (df + 0.5)) + 1 for term, df in doc_freq.items()}

    def count(self) -> int:
        return len(self._chunks)

    def query(
        self,
        query_texts: list[str],
        n_results: int,
        include: list[str] | None = None,
    ) -> dict[str, list[list[Any]]]:
        question = query_texts[0] if query_texts else ""
        q_tokens = tokens(question)
        q_counts = Counter(q_tokens)
        q_phrase = " ".join(q_tokens)
        scored = []
        for idx, chunk in enumerate(self._chunks):
            score = self._score(chunk, q_counts, q_phrase, question.lower())
            if score > 0:
                scored.append((score, idx, chunk))
        scored.sort(key=lambda item: (-item[0], item[1]))
        top = scored[:n_results]
        return {
            "ids": [[c.chunk_id for _, _, c in top]],
            "documents": [[c.text for _, _, c in top]],
            "metadatas": [[c.metadata for _, _, c in top]],
            "distances": [[0.0 for _ in top]],
        }

    def _score(
        self,
        chunk: Chunk,
        q_counts: Counter[str],
        q_phrase: str,
        question_lower: str,
    ) -> float:
        score = 0.0
        blob = f"{chunk.doc_title} {chunk.section_heading} {chunk.doc_slug} {chunk.text}".lower()
        for term, q_count in q_counts.items():
            idf = self._idf.get(term, 1.0)
            score += min(chunk.body_tokens.get(term, 0), 6) * idf * q_count
            score += chunk.heading_tokens.get(term, 0) * idf * 8
            score += chunk.title_tokens.get(term, 0) * idf * 4
            if term in chunk.doc_slug:
                score += idf * 3

        # Phrase and domain-specific boosts for short policy questions.
        if q_phrase and q_phrase in blob:
            score += 25
        boosts = {
            "gift": ("gift", "hospitality"),
            "vendor gift": ("gift", "hospitality"),
            "password": ("password", "mfa"),
            "incident": ("incident", "reporting"),
            "retention": ("retention",),
            "retained": ("data protection", "retention"),
            "routine hr": ("data protection", "retention"),
            "operational records": ("data protection", "retention"),
            "privacy": ("data subject", "requests"),
            "core hours": ("core hours",),
            "annual leave": ("annual leave",),
            "appeal": ("appeals",),
            "internet": ("expense categories", "reimbursement"),
            "three quote": ("three quote",),
            "risk score": ("risk scoring",),
            "30-60-90": ("30-60-90",),
            "new role": ("job requisition",),
            "posting": ("job requisition",),
            "pip": ("rating definitions",),
        }
        for trigger, targets in boosts.items():
            if trigger in question_lower:
                for target in targets:
                    if target in blob:
                        score += 30
        return score
