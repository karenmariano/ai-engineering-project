# Policy corpus for local + Render

Render and a fresh clone do **not** have access to paths on your laptop (e.g. `~/Downloads/...`).
Put the **same** pack you use locally here so it can be **committed** and indexed during the Render build:

```bash
# From the repo root (adjust source path if needed)
rsync -a --delete "${RAG_SOURCE:-$HOME/Downloads/rag_policy_corpus}/" "./data/corpus/"
```

Required for `pip install` / ingest on Render:

- `data/corpus/chunks/chunks.jsonl`

Then:

```bash
git add data/corpus
git commit -m "Add policy corpus for deployment"
```

*You can omit large PDF/HTML copies if you only rely on the JSONL; the app indexes `chunks/chunks.jsonl`.*
