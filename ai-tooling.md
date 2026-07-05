# AI Tooling

## Tools Used

- Codex was used to inspect the repository, clean generated files, initialize the project Git repository, and identify missing project documentation.
- Codex helped implement and validate the reproducible evaluation workflow in `scripts/evaluate.py`.
- Codex assisted with documentation updates for design choices, evaluation approach, setup, and repository hygiene.
- AI assistance was also used for debugging environment issues such as virtual environment activation, Git root scoping, ignored files, and embedding model initialization.

## What Worked Well

- Fast repo inspection made it easy to find documentation gaps, especially the placeholder design/evaluation and AI-tooling documents.
- Automated evaluation generation helped turn benchmark files into concrete metrics: groundedness, citation accuracy, top-1 retrieval, and latency.
- AI-assisted debugging caught an important benchmark mismatch where several expected chunk IDs were stale relative to the actual chunk manifest.
- The assistant helped keep local-only files such as `.env`, `.venv`, generated indexes, caches, and `.DS_Store` out of the Git commit.

## What Did Not Work Well

- Free LLM provider routes can be rate-limited, especially OpenRouter free models. The deployed app requires `LLM_API_KEY`; if a configured provider fails after retrieval, the app falls back to extractive cited answers so the user still sees a grounded response.
- Render free-tier workers timed out when an embedding model initialized during the first request. Switching to lexical retrieval removed that startup bottleneck.
- AI suggestions still required human review, especially for confirming that generated documentation accurately reflected the working code.
