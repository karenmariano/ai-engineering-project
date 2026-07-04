# Design and Evaluation

## Design Decisions

This project implements a Flask-based retrieval-augmented generation policy assistant. The system is intentionally small and reproducible: document ingestion, retrieval, answer generation, configuration, UI, and tests are separated into focused modules under `src/`, `scripts/`, `templates/`, and `tests/`.

### Corpus and Chunking

The project uses a legally safe synthetic company policy corpus committed under `data/corpus`. The corpus contains 15 policy/procedure documents, 135 section-level chunks, Markdown/HTML/PDF versions, and benchmark files. Section-level chunks were chosen because policy answers usually map to complete titled sections such as "Incident Reporting", "Annual Leave", or "Expense Categories". This keeps citations human-readable and avoids splitting policy rules across arbitrary token windows.

### Embeddings and Vector Store

Embeddings use `sentence-transformers/all-MiniLM-L6-v2`, a free local embedding model with a good speed/quality tradeoff for short policy sections. Chroma is used as the local persistent vector store because it works without managed infrastructure, persists indexes under `data/chroma`, and supports metadata-rich retrieval. The generated Chroma index is ignored by Git and rebuilt with:

```bash
python scripts/ingest.py --force
```

### Retrieval and Prompting

The app retrieves the top `RAG_TOP_K` chunks, defaulting to 8, and includes full citation metadata in every response. A lightweight keyword tie-breaker improves ranking for policy terms such as PTO, leave, benefits, and related HR terms. Retrieved chunks are injected into an OpenAI-compatible chat completion prompt with explicit instructions to answer only from context and list source chunk IDs.

### Guardrails

The RAG engine includes these guardrails:

- Empty questions are refused.
- Low-confidence retrievals are refused using an L2 distance threshold.
- Answers are capped by `RAG_MAX_ANSWER_CHARS`.
- Every successful answer returns citations and evidence snippets.
- If the configured LLM provider is missing, rate-limited, or unavailable, the app returns an extractive answer from the best cited section instead of failing the request.

### Web and API

The Flask app exposes:

- `/` - browser chat UI
- `/chat` - JSON API accepting `{"question": "..."}`
- `/health` - JSON health and indexed chunk count

The API response includes `answer`, `citations`, `snippets`, `latency_ms`, and refusal status.

### CI/CD and Deployment

GitHub Actions installs dependencies, imports the app, and runs `pytest` on push and pull request. `render.yaml` provides a Render blueprint that installs dependencies, verifies `data/corpus/chunks/chunks.jsonl`, builds the Chroma index, and starts the app with Gunicorn. Deployment is optional for the rubric, but the repository is structured so a Render deployment can be created from the committed corpus.

## Evaluation Approach

Evaluation is implemented in `scripts/evaluate.py` and writes results to `evaluation/results.md` and `evaluation/results.json`.

The evaluation uses 24 benchmark questions from `data/corpus/benchmarks`:

- 14 retrieval benchmark queries
- 10 short-answer QA benchmark questions

The evaluation disables live LLM calls so results are reproducible under free-tier quota limits. It evaluates the RAG system's retrieval, citation mapping, extractive answer grounding, and latency using the same Chroma index and `RAGEngine.answer()` path used by the app.

Metrics:

- Groundedness: answer is not refused, includes snippets, and cites the expected supporting chunk.
- Citation accuracy: the expected supporting chunk appears in the returned citations.
- Top-1 retrieval hit rate: the first returned citation is the expected supporting chunk.
- Latency: p50/p95 end-to-end answer time for the 24 benchmark questions after index/model initialization.

Run:

```bash
python scripts/ingest.py --force
python scripts/evaluate.py
```

## Evaluation Results

Latest local run:

- Questions: 24
- Corpus chunks indexed: 135
- Groundedness: 100.0%
- Citation accuracy: 100.0%
- Top-1 retrieval hit rate: 87.5%
- Latency p50: 7.5 ms
- Latency p95: 10.15 ms

See `evaluation/results.md` for the per-question table and `evaluation/results.json` for machine-readable output.
