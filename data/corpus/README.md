# RAG-Optimized Synthetic Policy Corpus

This package contains a legally safe, fully synthetic company-policy corpus designed for retrieval-augmented generation experiments.

## Design goals
- Stable document slugs and section IDs
- Heading-based chunk boundaries
- Explicit metadata in source files
- Cross-domain policy coverage
- Gold query and QA benchmark sets
- Multiple delivery formats: Markdown, HTML, PDF

## Directory layout
- `markdown/`: source documents with YAML front matter
- `html/`: browser-friendly versions
- `pdf/`: polished PDF renderings
- `chunks/chunks.jsonl`: one record per retrieval chunk
- `benchmarks/queries.jsonl`: retrieval benchmark queries
- `benchmarks/qa_pairs.jsonl`: short-form answer benchmark set
- `manifests/documents.csv`: document inventory
- `manifests/chunks.csv`: flat chunk inventory

## Suggested indexing strategy
Use each section as a base chunk. Preserve:
- `chunk_id`
- `doc_slug`
- `section_heading`
- `owner`
- full section text

For higher recall, add:
- title prefix
- section heading prefix
- sibling-section expansion at query time

## Corpus summary
- Documents: 15
- Chunks: 135
- Effective date: 2026-04-20
- Version: 3.0-rag
