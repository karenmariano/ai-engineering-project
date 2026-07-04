# Software Requirements Specification (SRS)

## 1. Introduction

### 1.1 Purpose
This document defines the software requirements for an AI Engineering project: a Retrieval-Augmented Generation (RAG) web application that answers questions about company policies and procedures with citations.

### 1.2 Scope
The system ingests a policy corpus, indexes document chunks in a vector store, retrieves relevant context for user queries, and generates grounded answers via an LLM. It includes:
- Document ingestion and indexing pipeline
- RAG inference pipeline with guardrails and citations
- Web user interface and API endpoints
- Health checks, reproducible environment setup, and CI/CD checks
- Evaluation workflow for answer quality and system latency

Optional scope:
- Public deployment to a free-tier cloud host (e.g., Render/Railway)

### 1.3 Definitions and Acronyms
- **RAG**: Retrieval-Augmented Generation
- **LLM**: Large Language Model
- **Top-k retrieval**: Returning the k most relevant chunks from vector search
- **Groundedness**: Answer content is fully supported by retrieved evidence
- **Citation accuracy**: Citations correctly point to supporting source passages
- **p50/p95 latency**: 50th/95th percentile response time

### 1.4 References
- AI Engineering Project Prompt and Rubric (Quantic)
- Repository files: `README.md`, `design-and-evaluation.md`, `ai-tooling.md`, `requirements.txt`

## 2. Overall Description

### 2.1 Product Perspective
The product is a standalone web application with batch/offline ingestion and online query serving. It uses a local or lightweight vector database and one or more external model APIs (embedding + generation), with environment-driven configuration.

### 2.2 Product Functions
- Parse and clean documents in PDF/HTML/Markdown/TXT formats
- Chunk documents with overlap and metadata tracking
- Generate embeddings and index vectors
- Retrieve top-k relevant chunks for each query
- Generate policy-grounded answers with required citations/snippets
- Refuse out-of-scope questions
- Enforce output length guardrails
- Expose `/`, `/chat`, and `/health` endpoints
- Run evaluation over curated question sets and output metrics

### 2.3 User Classes
- **End user**: asks policy questions through UI/API
- **Developer/operator**: configures models, runs ingestion/evaluation, deploys app
- **Evaluator/grader**: validates quality, citations, and reproducibility artifacts

### 2.4 Operating Environment
- OS: macOS/Linux/Windows (development)
- Runtime: Python 3.x in isolated virtual environment
- Dependencies: defined in `requirements.txt`
- Data store: local/lightweight vector DB (e.g., Chroma) or optional managed store
- Hosting (optional): Render/Railway free tier

### 2.5 Constraints
- Must use legally shareable corpus (no private/paid-protected documents required)
- Prefer free/zero-cost model/API tiers where feasible
- Must include citations for all answers
- Must provide reproducible setup instructions and deterministic settings where applicable

### 2.6 Assumptions and Dependencies
- Valid API keys/endpoints are available via environment variables
- Corpus size: approximately 5-20 files totaling 30-120 pages
- Model/API rate limits may affect throughput/latency

## 3. System Features and Functional Requirements

### 3.1 Environment and Reproducibility
- **FR-1**: System shall support setup in a virtual environment.
- **FR-2**: System shall list dependencies in `requirements.txt` (or equivalent).
- **FR-3**: System shall provide `README.md` with setup and run instructions.
- **FR-4**: System shall set fixed seeds where relevant (e.g., deterministic chunking/eval sampling).

### 3.2 Ingestion and Indexing
- **FR-5**: System shall ingest PDF, HTML, Markdown, and TXT files.
- **FR-6**: System shall parse and clean extracted text before chunking.
- **FR-7**: System shall chunk documents using a configurable strategy (heading- or token-based) with overlap.
- **FR-8**: System shall generate embeddings for all chunks using configured embedding model/API.
- **FR-9**: System shall persist vectors and chunk metadata to a vector store.
- **FR-10**: System shall track source metadata (document ID/title/path and chunk location) for citation.

### 3.3 Retrieval and Generation (RAG)
- **FR-11**: System shall perform top-k retrieval for each user question (k configurable).
- **FR-12**: System may support optional re-ranking before final context assembly.
- **FR-13**: System shall construct prompts that inject retrieved chunks and source identifiers.
- **FR-14**: System shall enforce refusal behavior for out-of-corpus queries.
- **FR-15**: System shall enforce maximum answer length.
- **FR-16**: System shall return citations for every answer, mapped to source IDs/titles.

### 3.4 Web Application and API
- **FR-17**: System shall expose `/` with a chat interface and question input box.
- **FR-18**: System shall expose `/chat` (POST) that accepts a question and returns:
  - generated answer text
  - citations (doc IDs/titles)
  - supporting snippets
- **FR-19**: System shall expose `/health` returning JSON status.
- **FR-20**: System shall return clear error responses for malformed/empty requests and upstream failures.

### 3.5 CI/CD and Build Validation
- **FR-21**: System shall include a GitHub Actions workflow on push/PR.
- **FR-22**: Workflow shall install dependencies and run a build/start validation check.
- **FR-23**: Workflow may include optional tests/smoke checks.
- **FR-24**: Optional deployment step may run after successful checks on main branch.

### 3.6 Evaluation and Reporting
- **FR-25**: System shall include an evaluation set of 15-30 policy questions.
- **FR-26**: System shall report groundedness percentage.
- **FR-27**: System shall report citation accuracy percentage.
- **FR-28**: System shall report latency p50/p95 over 10-20 queries.
- **FR-29**: System may report optional exact/partial match and ablation experiments.
- **FR-30**: Repository shall include a design/evaluation document and AI tooling usage summary.

## 4. External Interface Requirements

### 4.1 User Interface
- Web chat page at `/`
- Displays model answer, source citations, and evidence snippets
- Simple and clear policy QA workflow for non-technical users

### 4.2 API Interface (`/chat`)
- **Method**: POST
- **Request (JSON)**:
  - `question` (string, required)
- **Response (JSON)**:
  - `answer` (string)
  - `citations` (array of source references)
  - `snippets` (array of supporting text snippets)
  - `latency_ms` (optional numeric field)

### 4.3 Health Interface (`/health`)
- **Method**: GET
- **Response**: JSON status payload (e.g., `{"status":"ok"}`)

## 5. Non-Functional Requirements

### 5.1 Performance
- **NFR-1**: System shall measure and report p50/p95 end-to-end response latency.
- **NFR-2**: System should return answers fast enough for interactive chat use under free-tier constraints.

### 5.2 Reliability and Robustness
- **NFR-3**: System shall handle unsupported file formats or parse errors without crashing ingestion.
- **NFR-4**: System shall gracefully handle empty retrieval results and return safe fallback/refusal output.
- **NFR-5**: `/health` endpoint shall indicate service readiness.

### 5.3 Security and Privacy
- **NFR-6**: API keys and secrets shall be provided only through environment variables.
- **NFR-7**: Secrets shall not be committed to source control.
- **NFR-8**: Application shall only answer from approved corpus; no hidden data access behavior.

### 5.4 Maintainability
- **NFR-9**: Codebase shall be modular (ingestion, retrieval, generation, web app, evaluation).
- **NFR-10**: Configuration for model choice, chunking, and retrieval k shall be parameterized.

### 5.5 Reproducibility
- **NFR-11**: Repository shall include clear run instructions and dependency lock-in via requirements.
- **NFR-12**: Evaluation procedure shall be documented to allow repeatability.

## 6. Data Requirements

### 6.1 Input Corpus
- 5-20 coherent policy/procedure files
- 30-120 total pages
- Legal to include in repo or load at runtime

### 6.2 Stored Data
- Raw/cleaned text (optional intermediate artifacts)
- Chunked document units
- Embeddings and vector index entries
- Metadata linking chunks to source docs and locations
- Evaluation dataset and results artifacts

## 7. Acceptance Criteria (Rubric-Aligned)

To satisfy a high-quality submission:
- Working end-to-end RAG with mostly correct, grounded answers
- Accurate citations linked to supporting passages
- Functional ingestion/indexing over required corpus size
- Web interface and required endpoints (`/`, `/chat`, `/health`)
- CI workflow running on push/PR
- Documented design choices and evaluation results (groundedness, citation accuracy, latency)
- Clear demo walkthrough (features, architecture, evaluation, CI/CD evidence)

## 8. Submission Artifacts Checklist

Required repository artifacts:
- `README.md` (setup + run)
- `design-and-evaluation.md` or equivalent design/evaluation document
- `ai-tooling.md` (tools used and effectiveness)
- Source code, ingestion/indexing, RAG app, and evaluation scripts
- CI workflow configuration

Optional repository artifacts:
- Deployment link document (e.g., `deployed.md`)

Final course submission package:
- One PDF containing:
  - link to accessible GitHub repository (shared with `quantic-grader`)
  - link to 5-10 minute recorded demo video
