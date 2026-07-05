"""Run a small, reproducible RAG evaluation over the bundled policy benchmarks."""

from __future__ import annotations

import json
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Keep evaluation deterministic and inexpensive. This evaluates retrieval,
# citation accuracy, extractive groundedness, and end-to-end app latency without
# depending on a live chat model quota.
os.environ["LLM_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = ""
os.environ["REQUIRE_LLM"] = "false"
os.environ["RAG_CORPUS_DIR"] = str(ROOT / "data" / "corpus")

from src.config import chunks_jsonl_path, project_root  # noqa: E402
from src.rag import RAGEngine  # noqa: E402


ROOT = project_root()
BENCHMARK_DIR = ROOT / "data" / "corpus" / "benchmarks"
OUT_DIR = ROOT / "evaluation"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    vals = sorted(values)
    idx = (len(vals) - 1) * pct
    lo = int(idx)
    hi = min(lo + 1, len(vals) - 1)
    if lo == hi:
        return vals[lo]
    return vals[lo] + (vals[hi] - vals[lo]) * (idx - lo)


def normalize_expected(row: dict[str, Any]) -> list[str]:
    if "relevant_chunk_ids" in row:
        return [str(x) for x in row["relevant_chunk_ids"]]
    return [str(row["source_chunk_id"])]


def make_eval_rows() -> list[dict[str, Any]]:
    retrieval_rows = read_jsonl(BENCHMARK_DIR / "queries.jsonl")
    qa_rows = read_jsonl(BENCHMARK_DIR / "qa_pairs.jsonl")
    out: list[dict[str, Any]] = []
    for row in retrieval_rows:
        out.append(
            {
                "id": row["query_id"],
                "question": row["query"],
                "expected_chunk_ids": normalize_expected(row),
                "task": "retrieval",
            }
        )
    for row in qa_rows:
        out.append(
            {
                "id": row["id"],
                "question": row["question"],
                "gold_answer": row["answer"],
                "expected_chunk_ids": normalize_expected(row),
                "task": "qa",
            }
        )
    return out


def run() -> dict[str, Any]:
    if not chunks_jsonl_path().is_file():
        raise FileNotFoundError(f"Missing corpus chunks at {chunks_jsonl_path()}")

    engine = RAGEngine()
    rows = make_eval_rows()
    results: list[dict[str, Any]] = []
    latencies: list[float] = []

    for row in rows:
        t0 = time.perf_counter()
        answer = engine.answer(row["question"])
        latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        latencies.append(latency_ms)
        cited_ids = [c["chunk_id"] for c in answer.get("citations", [])]
        expected = row["expected_chunk_ids"]
        citation_hit = any(cid in cited_ids for cid in expected)
        top1_hit = bool(cited_ids) and cited_ids[0] in expected
        grounded = (not answer.get("refused")) and citation_hit and bool(answer.get("snippets"))
        results.append(
            {
                **row,
                "latency_ms": latency_ms,
                "cited_chunk_ids": cited_ids,
                "top1_hit": top1_hit,
                "citation_hit": citation_hit,
                "grounded": grounded,
                "answer_preview": str(answer.get("answer", ""))[:500],
            }
        )

    n = len(results)
    summary = {
        "questions": n,
        "corpus_chunks": sum(1 for _ in chunks_jsonl_path().open(encoding="utf-8")),
        "groundedness_pct": round(100 * sum(r["grounded"] for r in results) / n, 1),
        "citation_accuracy_pct": round(100 * sum(r["citation_hit"] for r in results) / n, 1),
        "top1_retrieval_pct": round(100 * sum(r["top1_hit"] for r in results) / n, 1),
        "latency_p50_ms": round(statistics.median(latencies), 2),
        "latency_p95_ms": round(percentile(latencies, 0.95), 2),
    }
    payload = {"summary": summary, "results": results}
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_markdown(summary, results)
    return payload


def write_markdown(summary: dict[str, Any], results: list[dict[str, Any]]) -> None:
    lines = [
        "# Evaluation Results",
        "",
        "Evaluation uses the bundled synthetic policy corpus benchmarks in `data/corpus/benchmarks`.",
        "The run disables live LLM calls so the metrics are reproducible under free-tier quota limits; answers are extractive from retrieved cited chunks.",
        "",
        "## Summary",
        "",
        f"- Questions: {summary['questions']}",
        f"- Corpus chunks indexed: {summary['corpus_chunks']}",
        f"- Groundedness: {summary['groundedness_pct']}%",
        f"- Citation accuracy: {summary['citation_accuracy_pct']}%",
        f"- Top-1 retrieval hit rate: {summary['top1_retrieval_pct']}%",
        f"- Latency p50: {summary['latency_p50_ms']} ms",
        f"- Latency p95: {summary['latency_p95_ms']} ms",
        "",
        "## Per-Question Results",
        "",
        "| ID | Task | Expected Chunk | Top Citation | Citation Hit | Grounded | Latency ms |",
        "| --- | --- | --- | --- | --- | --- | ---: |",
    ]
    for row in results:
        expected = ", ".join(row["expected_chunk_ids"])
        top = row["cited_chunk_ids"][0] if row["cited_chunk_ids"] else ""
        lines.append(
            f"| {row['id']} | {row['task']} | `{expected}` | `{top}` | "
            f"{row['citation_hit']} | {row['grounded']} | {row['latency_ms']} |"
        )
    lines.append("")
    (OUT_DIR / "results.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    data = run()
    print(json.dumps(data["summary"], indent=2))
