"""RAG: retrieve policy chunks, then generate or extractive answer with citations."""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from src.config import (
    CITATION_SNIPPET_MAX_CHARS,
    EXTRACTIVE_MAX_CHARS,
    LLM_MAX_TOKENS,
    LLM_TIMEOUT_SECONDS,
    RAG_MAX_ANSWER_CHARS,
    RAG_MAX_L2_DISTANCE,
    RAG_TOP_K,
    llm_api_key,
    llm_model,
    openai_base_url,
)
from src.ingest import get_collection

log = logging.getLogger(__name__)
_llm_key_missing_logged: bool = False

OUT_OF_SCOPE = (
    "I can only answer questions that are supported by the indexed company policy "
    "documents. I could not find enough relevant information to answer that question."
)


@dataclass
class Citation:
    chunk_id: str
    doc_title: str
    section_heading: str
    doc_slug: str
    text: str

    @property
    def snippet(self) -> str:
        t = self.text
        cap = CITATION_SNIPPET_MAX_CHARS
        if len(t) <= cap:
            return t
        return t[:cap] + "…"

    def to_dict(self) -> dict[str, str]:
        return {
            "chunk_id": self.chunk_id,
            "doc_title": self.doc_title,
            "section_heading": self.section_heading,
            "doc_slug": self.doc_slug,
            "snippet": self.snippet,
        }


class RAGEngine:
    def __init__(self, collection: Any | None = None) -> None:
        self._collection = collection

    @property
    def collection(self) -> Any:
        if self._collection is None:
            self._collection = get_collection()
        return self._collection

    def retrieve(self, question: str) -> tuple[list[Citation], list[float] | None]:
        res = self.collection.query(
            query_texts=[question],
            n_results=RAG_TOP_K,
            include=["documents", "metadatas", "distances"],
        )
        ids_list = (res.get("ids") or [[]])[0]
        dist_list = (res.get("distances") or [[]])[0] if res.get("distances") else None
        docs_list = (res.get("documents") or [[]])[0]
        meta_list = (res.get("metadatas") or [[]])[0]
        cits: list[Citation] = []
        for i, cid in enumerate(ids_list):
            m = dict(meta_list[i] or {}) if i < len(meta_list) else {}
            text = (docs_list[i] if i < len(docs_list) else "") or ""
            cits.append(
                Citation(
                    chunk_id=str(m.get("chunk_id") or cid),
                    doc_title=str(m.get("doc_title") or ""),
                    section_heading=str(m.get("section_heading") or ""),
                    doc_slug=str(m.get("doc_slug") or ""),
                    text=text,
                )
            )
        return cits, dist_list

    def _gated(
        self, cits: list[Citation], distances: list[float] | None
    ) -> tuple[bool, str | None]:
        if not cits:
            return False, OUT_OF_SCOPE
        if distances and distances[0] is not None and float(distances[0]) > RAG_MAX_L2_DISTANCE:
            return False, OUT_OF_SCOPE
        return True, None

    def _build_context(self, cits: list[Citation]) -> str:
        parts: list[str] = []
        for c in cits:
            label = f"[{c.doc_title} — {c.section_heading}] (chunk_id={c.chunk_id})"
            parts.append(f"{label}\n{c.text.strip()}\n")
        return "\n---\n".join(parts).strip()

    def _llm(self, question: str, context: str) -> str:
        key = llm_api_key()
        if not key:
            raise RuntimeError("No API key for LLM")
        client = OpenAI(
            api_key=key,
            base_url=openai_base_url(),
            timeout=LLM_TIMEOUT_SECONDS,
            max_retries=0,
        )
        system = (
            "You are a company policy assistant. Answer ONLY using the CONTEXT below. "
            "If the answer is not in the context, say you cannot find it in the policies. "
            "For policy questions, be complete: include every relevant rule, number, "
            "threshold, and approval or timing requirement from the context—do not stop "
            "after one sentence if more rules apply. At the end, list the chunk_id values "
            "you used as Sources: chunk_id1, chunk_id2."
        )
        user = f"CONTEXT:\n{context}\n\nQUESTION:\n{question}\n"
        resp = client.chat.completions.create(
            model=llm_model(),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=LLM_MAX_TOKENS,
            temperature=0.2,
        )
        return (resp.choices[0].message.content or "").strip()

    def _short_err(self, exc: Exception) -> str:
        s = str(exc).strip()
        if len(s) > 220:
            s = s[:220] + "…"
        return s

    def _llm_failure_note(self, exc: Exception) -> str:
        s = str(exc)
        s_low = s.lower()
        base = openai_base_url().lower()
        is_openrouter = "openrouter" in base
        is_google = "generativelanguage" in base or "google" in base

        if "429" in s or "quota" in s_low or "resource_exhausted" in s_low or "rate limit" in s_low:
            if is_openrouter:
                return (
                    "OpenRouter returned HTTP 429 (rate limit or free-tier cap). This is not a bug in "
                    "this app. Try: wait a few minutes, pick another free model (e.g. a smaller "
                    "`...:free` id), or check usage at openrouter.ai. Below is an extractive answer."
                )
            if is_google:
                return (
                    "Google Gemini returned 429 (quota or rate limit). Check Google AI Studio usage, "
                    "wait, or adjust billing. Below is an extractive snippet."
                )
            return (
                "The LLM API returned HTTP 429 (rate limit or quota). Wait and retry, or check your "
                "provider’s limits. Below is an extractive answer."
            )
        if "401" in s or "403" in s or ("invalid" in s_low and "key" in s_low):
            hint = "AI Studio" if is_google else ("OpenRouter" if is_openrouter else "your provider")
            return f"{self._short_err(exc)} Verify `LLM_API_KEY` and {hint} key settings."
        if "connection error" in s_low or "api connection" in s_low:
            provider = "OpenRouter" if is_openrouter else ("Google Gemini" if is_google else "the LLM provider")
            return (
                f"{self._short_err(exc)} Could not connect to {provider}. Verify "
                "`OPENAI_BASE_URL`, `LLM_MODEL`, and that `LLM_API_KEY` is a valid active key. "
                "Free provider routes can also be temporarily unavailable. Showing extractive text "
                "from retrievals instead."
            )
        return (
            f"{self._short_err(exc)} Showing extractive text from retrievals instead. "
            "If this persists, check `OPENAI_BASE_URL` and `LLM_MODEL`."
        )

    def _rerank_citations(self, cits: list[Citation], question: str) -> list[Citation]:
        """Tie-break retrieval with light keyword overlap (e.g. PTO -> leave policy)."""
        if len(cits) < 2:
            return cits
        q = question.lower()
        q_words = {w for w in re.findall(r"\w+", q) if len(w) > 2}
        ptoish = bool(
            re.search(r"\bpto\b|paid time off|paid leave|time off|vacation|sick (day|leave)?|absence|holiday|benefit|parental|bereavement", q)
        )

        def score_val(i: int) -> int:
            c = cits[i]
            blob = f"{c.doc_title} {c.section_heading} {c.text} {c.doc_slug}".lower()
            slug = c.doc_slug.lower()
            s = 0
            for w in q_words:
                if w in blob:
                    s += 2
            if ptoish:
                if "leave" in slug or "benefit" in slug:
                    s += 12
                for t in ("leave", "pto", "vacation", "benefit", "holiday", "sick", "time off", "absence", "accrual"):
                    if t in q and t in blob:
                        s += 3
            return s

        if max(score_val(i) for i in range(len(cits))) == 0:
            return cits
        order = sorted(range(len(cits)), key=lambda i: (-score_val(i), i))
        return [cits[i] for i in order]

    def _truncate_text(self, text: str, cap: int) -> str:
        t = text.strip()
        if len(t) <= cap:
            return t
        cut = t[:cap]
        if " " in cut:
            cut = cut.rsplit(" ", 1)[0]
        return cut + "…"

    def _extractive(
        self,
        cits: list[Citation],
        question: str,
        *,
        llm_error: Exception | None = None,
    ) -> tuple[str, str | None]:
        head = cits[0]
        body_text = self._truncate_text(head.text, EXTRACTIVE_MAX_CHARS) or head.snippet
        main = (
            f"Based on **{head.doc_title}** — *{head.section_heading}*:\n\n{body_text}\n"
        )
        if llm_error is not None:
            return main.strip(), self._llm_failure_note(llm_error)
        return main.strip(), (
            "No LLM key in environment. Set `LLM_API_KEY` or `OPENAI_API_KEY` (and, for Google "
            "Gemini, `OPENAI_BASE_URL` + `LLM_MODEL`). The app looks for a `.env` file in the "
            "project root."
        )

    def _trim(self, s: str) -> str:
        s = s.strip()
        if len(s) > RAG_MAX_ANSWER_CHARS:
            return s[: RAG_MAX_ANSWER_CHARS] + "…"
        return s

    def answer(self, question: str) -> dict[str, Any]:
        q = (question or "").strip()
        t0 = time.perf_counter()
        if not q:
            return {
                "answer": OUT_OF_SCOPE,
                "citations": [],
                "snippets": [],
                "latency_ms": 0.0,
                "refused": True,
            }
        cits, distances = self.retrieve(q)
        ok, err = self._gated(cits, distances)
        if not ok:
            ms = (time.perf_counter() - t0) * 1000.0
            return {
                "answer": err or OUT_OF_SCOPE,
                "citations": [],
                "snippets": [],
                "latency_ms": round(ms, 2),
                "refused": True,
            }
        cits = self._rerank_citations(cits, q)
        context = self._build_context(cits)
        notice: str | None = None
        if llm_api_key():
            try:
                raw = self._llm(q, context)
            except Exception as e:  # noqa: BLE001
                log.exception("LLM call failed; falling back to extractive")
                raw, notice = self._extractive(cits, q, llm_error=e)
        else:
            global _llm_key_missing_logged
            if not _llm_key_missing_logged:
                _llm_key_missing_logged = True
                log.info(
                    "No LLM_API_KEY/OPENAI_API_KEY: using extractive answers. "
                    "Set keys in a .env file at the project root (see README)."
                )
            raw, notice = self._extractive(cits, q)
        ms = (time.perf_counter() - t0) * 1000.0
        out: dict[str, Any] = {
            "answer": self._trim(raw),
            "citations": [c.to_dict() for c in cits],
            "snippets": [c.snippet for c in cits],
            "latency_ms": round(ms, 2),
            "refused": False,
        }
        if notice:
            out["notice"] = notice
        return out
