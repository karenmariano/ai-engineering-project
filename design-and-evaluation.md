# Design and Evaluation

## Design Decisions

This project implements a Flask-based retrieval-augmented generation policy assistant. The system is intentionally small and reproducible: document ingestion, retrieval, answer generation, configuration, UI, and tests are separated into focused modules under `src/`, `scripts/`, `templates/`, and `tests/`.

### Corpus and Chunking

The project uses a legally safe synthetic company policy corpus committed under `data/corpus`. The corpus contains 15 policy/procedure documents, 135 section-level chunks, Markdown/HTML/PDF versions, and benchmark files. Section-level chunks were chosen because policy answers usually map to complete titled sections such as "Incident Reporting", "Annual Leave", or "Expense Categories". This keeps citations human-readable and avoids splitting policy rules across arbitrary token windows.

### Retrieval Store

The deployed app uses a fast lexical retriever over the committed `data/corpus/chunks/chunks.jsonl` file. This keeps Render free-tier requests lightweight because no embedding model is downloaded or initialized during `/chat`. The retriever scores section text, document titles, headings, phrase overlap, policy-specific terms, and numeric tokens, then returns the top `RAG_TOP_K` cited chunks.

The corpus can be validated with:

```bash
python scripts/ingest.py --force
```

### Retrieval and Prompting

The app retrieves the top `RAG_TOP_K` chunks, defaulting to 8, and includes full citation metadata in every response. Retrieved chunks are injected into an OpenAI-compatible chat completion prompt with explicit instructions to answer only from context and list source chunk IDs.

### Guardrails

The RAG engine includes these guardrails:

- Empty questions are refused.
- Low-confidence retrievals are refused using an L2 distance threshold.
- Answers are capped by `RAG_MAX_ANSWER_CHARS`.
- Every successful answer returns citations and evidence snippets.
- If the deployed app is missing `LLM_API_KEY`/`OPENAI_API_KEY` and `REQUIRE_LLM=true`, `/chat` returns a clear configuration error.
- If a configured LLM provider is rate-limited or unavailable after retrieval, the app returns an extractive answer from the best cited section instead of failing the request.

### Web and API

The Flask app exposes:

- `/` - browser chat UI
- `/chat` - JSON API accepting `{"question": "..."}`
- `/health` - JSON health and indexed chunk count

The API response includes `answer`, `citations`, `snippets`, `latency_ms`, and refusal status.

### CI/CD and Deployment

GitHub Actions installs dependencies, imports the app, and runs `pytest` on push and pull request. `render.yaml` provides a Render blueprint that installs dependencies, verifies `data/corpus/chunks/chunks.jsonl`, and starts the app with Gunicorn.

## Evaluation Approach

Evaluation is implemented in `scripts/evaluate.py` and writes results to `evaluation/results.md` and `evaluation/results.json`.

The evaluation uses 24 benchmark questions from `data/corpus/benchmarks`:

- 14 retrieval benchmark queries
- 10 short-answer QA benchmark questions

The evaluation sets `REQUIRE_LLM=false` and disables live LLM calls so results are reproducible under free-tier quota limits. It evaluates the RAG system's retrieval, citation mapping, extractive answer grounding, and latency using the same retriever and `RAGEngine.answer()` path used by the app.

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
- Latency p50: 0.62 ms
- Latency p95: 0.94 ms

See `evaluation/results.md` for the per-question table and `evaluation/results.json` for machine-readable output.
