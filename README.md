# AI Engineering Project

RAG (Retrieval-Augmented Generation) app over a **pre-chunked** policy corpus. It loads
`chunks/chunks.jsonl` (section-level chunks), retrieves top `k` policy sections per question,
and returns an LLM answer with **citations and snippets** via a small Flask UI and JSON API.

## Policy corpus (yours)

This project is wired for a corpus layout like `rag_policy_corpus`:

- `chunks/chunks.jsonl` — one JSON object per chunk with `chunk_id`, `doc_title`, `section_heading`, `text`, etc.
- Optional: `markdown/`, `html/`, `pdf/` (not required for indexing if you use the JSONL)

**Set the corpus root** (the folder that *contains* `chunks/chunks.jsonl`):

```bash
export RAG_CORPUS_DIR="/Users/karenmariano/Downloads/rag_policy_corpus"
```

Or symlink it into the repo (no `export` needed):

```bash
ln -snf "/Users/karenmariano/Downloads/rag_policy_corpus" "data/corpus"
```

Copy `.env.example` to `.env` and adjust `RAG_CORPUS_DIR` as needed. If `python-dotenv` is installed, the app will load `.env` on import.

## Quickstart

1. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Validate/load the corpus. From the repo root:

   ```bash
   python scripts/ingest.py
   ```

   Equivalently: `python -m scripts.ingest`.

3. Run the app:

   ```bash
   python -m src.app
   ```

   - **Web chat:** <http://127.0.0.1:5000/>  
   - **API:** `POST /chat` with JSON `{"question":"..."}`  
   - **Health:** `GET /health`  

## Required: LLM answers (OpenAI-compatible)

For the deployed chat app, `LLM_API_KEY` or `OPENAI_API_KEY` is required. The app calls an OpenAI-compatible `chat.completions` API: `OPENAI_BASE_URL` (default `https://api.openai.com/v1` if unset) and `LLM_MODEL`. If no key is set and `REQUIRE_LLM=true` (the Render default), `/chat` returns a clear 503 configuration error.

**Google AI Studio (Gemini)** — create a key in [AI Studio](https://aistudio.google.com/apikey), then in `.env` (copy from `.env.example`):

```bash
LLM_API_KEY=your_key_here
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
LLM_MODEL=gemini-2.0-flash
```

`python-dotenv` loads **`<project>/.env`** from the project root (see `src/config.py`) so the key is found even if your **shell’s current directory** is not the repo. **Restart the Flask process** after editing `.env`.

If the answer still says the LLM failed, read the new parenthetical (it includes the API error). Often that means a wrong `LLM_MODEL` / base URL, or a network issue—not a missing key.

**Why the first request can be slow:** the first Gemini/OpenRouter call can be cold. Later requests are usually faster.

**If you see HTTP 429:** that is a **rate limit or quota** at whatever provider is in `OPENAI_BASE_URL` (Gemini, OpenRouter free tier, etc.), not a bug in this app. The UI will show an **extractive** answer. For **OpenRouter**, large free models (e.g. 70B) are often throttled; try a smaller `:free` model, wait, or check [OpenRouter](https://openrouter.ai/) usage. For **Gemini**, use AI Studio billing/quotas.

**OpenRouter** — [create a key](https://openrouter.ai/keys) and set:

```bash
LLM_API_KEY=sk-or-v1-...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=cohere/north-mini-code:free
```

`LLM_MODEL` must be a concrete route from [OpenRouter models](https://openrouter.ai/models), not a placeholder such as `openrouter/free`. Free routes change over time; if OpenRouter returns “No endpoints found”, pick a currently listed `:free` model and update the Render environment variable.

**Security:** never commit `.env` or paste live keys into chat, issue trackers, or screen recordings. If a key is exposed, revoke it in the provider’s dashboard and create a new one.

The `/chat` JSON may include an optional **`notice`** (e.g. LLM error or extractive fallback); the web UI renders it below the answer so users can tell when the provider fell back.

For local development or reproducible evaluation without API quota, set:

```bash
REQUIRE_LLM=false
```

## Project layout

- `src/app.py` — Flask routes: `/`, `/chat`, `/health`
- `src/ingest.py` — validate/load `chunks/chunks.jsonl`
- `src/lexical.py` — fast lexical retrieval over policy chunks
- `src/rag.py` — retrieval + generation / extractive fallback
- `src/config.py` — paths, `RAG_CORPUS_DIR`, retrieval thresholds
- `scripts/ingest.py` — CLI for indexing
- `software-requirements-specification.md` — SRS
- `design-and-evaluation.md` — design choices + evaluation metrics
- `ai-tooling.md` — AI tool usage (submission)

## Answer length (defaults increased for full policy sections)

- Final `answer` is capped at **`RAG_MAX_ANSWER_CHARS`** (default **12000**).
- LLM output uses **`LLM_MAX_TOKENS`** (default **2000**).
- Extractive fallback uses the best-matching **whole section** up to **`EXTRACTIVE_MAX_CHARS`** (default **10000**), not a short sentence cap.
- Citation `snippet` in JSON uses **`CITATION_SNIPPET_MAX_CHARS`** (default **2000**). Override any via `.env`.

## Reproducibility

- `RAG_SEED` is reserved for any deterministic eval sampling you add (default `42`).
- Retrieval uses `data/corpus/chunks/chunks.jsonl` directly by default, so Render does not need to download an embedding model at request time.

## Tests and CI

```bash
pytest -q
```

GitHub Actions installs dependencies, imports the app, and runs `pytest`.

## Evaluation

The repository includes the synthetic policy corpus and benchmark questions under `data/corpus`.
Run the reproducible evaluation after building the index:

```bash
python scripts/ingest.py --force
python scripts/evaluate.py
```

Latest results are committed in `evaluation/results.md`:

- Groundedness: 100.0%
- Citation accuracy: 100.0%
- Top-1 retrieval hit rate: 87.5%
- Latency p50/p95: 0.62 ms / 0.94 ms
