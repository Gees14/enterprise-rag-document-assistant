# TASKS.md — Implementation Checklist

## Phase 1: Project Setup & Documentation
- [x] Create project directory structure
- [x] Write CLAUDE.md (AI session guidance)
- [x] Write PROJECT_SPEC.md (product spec)
- [x] Write ARCHITECTURE.md (system design + Mermaid diagrams)
- [x] Write TASKS.md (this file)
- [x] Write DECISIONS.md (architecture decision records)
- [x] Write .env.example
- [x] Write .gitignore

## Phase 2: Backend — Core Infrastructure
- [x] `backend/requirements.txt`
- [x] `backend/app/core/config.py` — pydantic-settings configuration
- [x] `backend/app/core/logging.py` — structured logging setup
- [x] `backend/app/core/errors.py` — custom exceptions + global handler
- [x] `backend/app/models/domain.py` — domain models + DocumentRepository
- [x] `backend/app/main.py` — FastAPI app with middleware and routers

## Phase 2: Backend — Schemas
- [x] `backend/app/schemas/document.py`
- [x] `backend/app/schemas/chat.py`
- [x] `backend/app/schemas/evaluation.py`

## Phase 2: Backend — Services
- [x] `backend/app/services/document_loader.py` — PDF text extraction
- [x] `backend/app/services/chunker.py` — overlapping text chunking
- [x] `backend/app/services/embeddings.py` — sentence-transformers embeddings
- [x] `backend/app/services/vector_store.py` — ChromaDB integration
- [x] `backend/app/services/retriever.py` — retrieval orchestration
- [x] `backend/app/services/reranker.py` — score-based reranking
- [x] `backend/app/services/generator.py` — LLM generation + fallback
- [x] `backend/app/services/evaluator.py` — RAG evaluation metrics

## Phase 2: Backend — API Routes
- [x] `backend/app/api/health.py` — GET /health, GET /health/ready
- [x] `backend/app/api/documents.py` — document CRUD + indexing
- [x] `backend/app/api/chat.py` — POST /chat/query
- [x] `backend/app/api/evaluation.py` — POST /eval/run, GET /eval/results

## Phase 2: Backend — Data
- [x] `backend/data/eval/questions.json` — sample evaluation questions

## Phase 3: Backend Tests
- [x] `backend/tests/conftest.py` — shared fixtures
- [x] `backend/tests/test_health.py`
- [x] `backend/tests/test_chunker.py`
- [x] `backend/tests/test_document_loader.py`
- [x] `backend/tests/test_retriever.py`
- [x] `backend/tests/test_evaluator.py`

## Phase 4: Frontend
- [x] `frontend/package.json`
- [x] `frontend/tsconfig.json`
- [x] `frontend/vite.config.ts`
- [x] `frontend/tailwind.config.js`
- [x] `frontend/index.html`
- [x] `frontend/src/types/index.ts`
- [x] `frontend/src/services/api.ts`
- [x] `frontend/src/components/Layout.tsx`
- [x] `frontend/src/components/UploadPanel.tsx`
- [x] `frontend/src/components/DocumentList.tsx`
- [x] `frontend/src/components/ChatPanel.tsx`
- [x] `frontend/src/components/CitationCard.tsx`
- [x] `frontend/src/components/EvaluationDashboard.tsx`
- [x] `frontend/src/pages/Dashboard.tsx`
- [x] `frontend/src/pages/Evaluation.tsx`
- [x] `frontend/src/App.tsx`
- [x] `frontend/src/main.tsx`

## Phase 5: DevOps
- [x] `backend/Dockerfile`
- [x] `frontend/Dockerfile`
- [x] `docker-compose.yml`
- [x] `Makefile`
- [x] `.github/workflows/ci.yml`

## Phase 6: Documentation
- [x] `README.md` — comprehensive project README
- [x] `backend/README.md`
- [x] `frontend/README.md`

---

## Future Improvements

- [ ] Add streaming LLM responses via Server-Sent Events
- [ ] Support non-PDF formats (DOCX, HTML, Markdown)
- [ ] Add cross-encoder reranking (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`)
- [ ] Add Qdrant as an alternative vector store backend
- [ ] Add persistent metadata database (SQLite or PostgreSQL)
- [ ] Add document deduplication via content hash
- [ ] Add multi-document filtering in queries
- [ ] Add user authentication (JWT)
- [ ] Add query history / conversation memory
- [ ] Add LLM provider selector in UI (OpenAI / Anthropic / Ollama)
- [ ] Add bulk evaluation with configurable question sets
- [ ] Add latency histogram and p95 monitoring
- [ ] Add Prometheus metrics endpoint
- [ ] Add OpenTelemetry tracing
