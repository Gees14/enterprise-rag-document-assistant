# DECISIONS.md — Architecture Decision Records

## ADR-001: FastAPI as the Backend Framework

**Status:** Accepted

**Context:**
We need a Python web framework for the backend. The options considered were Flask, Django REST Framework, and FastAPI.

**Decision:** FastAPI

**Reasons:**
- Native async support aligns with I/O-heavy RAG workloads (embeddings, LLM calls).
- Automatic OpenAPI documentation at `/docs` — useful for portfolio demos.
- First-class Pydantic integration for request/response validation.
- Type hints throughout — matches the type-safe approach of the project.
- Fastest growing Python web framework; highly relevant for AI Engineer roles.

**Alternatives Considered:**
- Flask: No built-in async, no Pydantic, no auto-docs. Fine for simple APIs, not ideal here.
- Django REST Framework: Too heavy for a single-service RAG API. Adds ORM and admin overhead.

**Consequences:**
- Requires Python 3.8+; we use 3.11+ for best performance.
- Uvicorn is needed as the ASGI server.

---

## ADR-002: ChromaDB as the Vector Database

**Status:** Accepted

**Context:**
We need a vector database to store chunk embeddings and perform approximate nearest-neighbor queries. Options considered: ChromaDB, Qdrant, FAISS, Pinecone.

**Decision:** ChromaDB (embedded/persistent mode)

**Reasons:**
- Zero infrastructure: runs embedded inside the FastAPI process; no separate service needed.
- Persistent: data survives restarts via `PersistentClient`.
- Simple Python API that matches the project's complexity level.
- Supports metadata filtering — useful for multi-document scenarios.
- Active development with a clear upgrade path to client-server mode.

**Alternatives Considered:**
- Qdrant: Excellent production vector DB, but requires a separate Docker container, adding deployment complexity.
- FAISS: No persistence out of the box; requires manual serialization; no metadata.
- Pinecone: Hosted-only; requires API key; not suitable for an offline-capable portfolio project.
- pgvector: Requires PostgreSQL; adds database dependency we want to avoid at this scope.

**Future Migration Path:**
Switch `vector_store.py` to use `qdrant-client` if the project scales to multi-user or requires distributed deployment.

---

## ADR-003: sentence-transformers for Local Embeddings

**Status:** Accepted

**Context:**
We need to generate dense vector embeddings for document chunks and queries. Options: sentence-transformers (local), OpenAI Embeddings API, Cohere Embeddings.

**Decision:** sentence-transformers, model `all-MiniLM-L6-v2` by default

**Reasons:**
- Works completely offline with no API key required.
- `all-MiniLM-L6-v2` is 384-dimensional, fast, and well-benchmarked on semantic search tasks.
- Configurable: users can swap to any sentence-transformers model via `EMBEDDING_MODEL` env var.
- Demonstrates knowledge of local ML model deployment — a key AI Engineer skill.
- No per-token costs.

**Alternatives Considered:**
- OpenAI `text-embedding-3-small`: Better quality, but requires API key and incurs costs. Not offline-capable.
- Cohere Embeddings: Same issue — requires API key.
- FastEmbed (Qdrant): Good performance, but tight coupling to Qdrant ecosystem.

**Tradeoffs:**
- Model cold-start adds ~5s to the first request.
- Quality slightly below OpenAI embeddings on general benchmarks.
- The model name is configurable to allow upgrading to `all-mpnet-base-v2` or similar.

---

## ADR-004: Retrieval-Only Fallback When No LLM Key is Set

**Status:** Accepted

**Context:**
The system should be usable without a paid LLM API key. We need a strategy for this case.

**Decision:** Return the top retrieved chunks as the "answer" when no OpenAI API key is configured.

**Reasons:**
- Makes the system usable to anyone who clones the repo.
- Demonstrates understanding that retrieval alone has value without generation.
- Prevents the system from hallucinating when no LLM is available.
- Portfolio-friendly: evaluators can test the full system without API keys.

**Implementation:**
In `generator.py`:
- If `settings.OPENAI_API_KEY` is None or empty: assemble the top chunk texts as the answer, set confidence from the top retrieval score.
- If API key is set: call the OpenAI-compatible API with the retrieved context.

---

## ADR-005: Docker for Local Development

**Status:** Accepted

**Context:**
We need a consistent way to run the full stack locally across different developer machines.

**Decision:** Docker + docker-compose

**Reasons:**
- Eliminates "works on my machine" issues for the portfolio reviewer.
- Industry standard for containerized development.
- Easy to add more services (Qdrant, Redis) later without changing developer workflow.
- Demonstrates DevOps knowledge relevant to MLOps Engineer roles.

**Alternatives Considered:**
- Virtual environments only: simple, but doesn't containerize the frontend or coordinate services.
- Nix / devenv: Too niche for a portfolio project.

---

## ADR-006: React + TypeScript + Vite + Tailwind for Frontend

**Status:** Accepted

**Context:**
We need a frontend UI. Options: plain HTML/JS, React, Vue, Next.js.

**Decision:** React 18 + TypeScript + Vite + Tailwind CSS

**Reasons:**
- React is the most common frontend framework in AI/ML product companies.
- TypeScript prevents runtime errors from API contract mismatches.
- Vite provides near-instant HMR and fast builds.
- Tailwind enables rapid, consistent styling without writing custom CSS.
- This stack matches what frontend-capable AI engineers are expected to know.

**Alternatives Considered:**
- Next.js: Adds SSR complexity not needed for a local SPA backed by a REST API.
- Vue: Good, but less common in AI/data product companies.
- Plain HTML: Insufficient for demonstrating engineering depth.

---

## ADR-007: pdfplumber for PDF Text Extraction

**Status:** Accepted

**Context:**
We need to extract text from PDF files. Options: pdfplumber, pypdf (PyPDF2), pdfminer, pymupdf.

**Decision:** pdfplumber

**Reasons:**
- More reliable text extraction than pypdf for complex PDF layouts.
- Page-level API matches our data model (we track page numbers per chunk).
- Handles tables and multi-column layouts better than alternatives.
- Pure Python, no system dependencies.

**Alternatives Considered:**
- pypdf: Lighter weight but less reliable on complex PDFs.
- pymupdf (fitz): Excellent quality but has a different license (AGPL) that could be a concern.
- pdfminer: Low-level; pdfplumber is built on top of it with a better API.

**Limitation:**
Neither pdfplumber nor alternatives can extract text from scanned (image-only) PDFs. OCR support (Tesseract) is a future improvement.

---

## ADR-008: JSON File for Document Metadata Storage

**Status:** Accepted (with known limitations)

**Context:**
We need to persist document metadata (id, filename, status, chunk count) across restarts.

**Decision:** JSON file at `data/documents.json`

**Reasons:**
- Zero dependencies — no database to install or configure.
- Sufficient for single-user local use.
- Simple to inspect and debug.
- Portfolio reviewers can see the data without needing a database client.

**Alternatives Considered:**
- SQLite: Better for concurrent access; slight overhead.
- PostgreSQL: Requires Docker service; overkill for this scope.

**Known Limitation:**
Concurrent writes are not safe. This is acceptable for local single-user use. A production system would use SQLite (via SQLAlchemy + Alembic) at minimum.

**Future Migration Path:**
Replace `DocumentRepository` in `models/domain.py` with a SQLAlchemy repository pattern. The service layer does not need to change.
