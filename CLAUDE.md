# CLAUDE.md — Enterprise RAG Document Assistant

This file guides future Claude Code sessions working on this repository.
Read it fully before modifying any code.

---

## Project Purpose

A production-quality Retrieval-Augmented Generation (RAG) system that allows users to:
1. Upload PDF documents
2. Index them into a vector database (ChromaDB)
3. Ask natural language questions
4. Receive grounded answers with citations to the original document chunks

This project is a portfolio demonstrator for AI/ML and full-stack engineering roles.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, Pydantic v2 |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2 by default) |
| Vector DB | ChromaDB (persistent, local) |
| PDF Extraction | pdfplumber |
| LLM Generation | OpenAI-compatible API (optional) |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| DevOps | Docker, docker-compose, Makefile, GitHub Actions |
| Testing | pytest, pytest-asyncio |

---

## Architecture Overview

```
PDF Upload → Text Extraction → Chunking → Embeddings → ChromaDB
                                                            ↓
User Question → Query Embedding → Vector Retrieval → Reranking → LLM Generation → Answer + Citations
```

Backend modules live in `backend/app/`:
- `api/` — FastAPI route handlers (thin, no business logic)
- `core/` — Config, logging, error handling
- `schemas/` — Pydantic request/response models
- `models/` — Domain models and in-memory document registry
- `services/` — All business logic (extraction, chunking, embeddings, etc.)

Frontend modules live in `frontend/src/`:
- `components/` — Reusable UI components
- `pages/` — Route-level page components
- `services/api.ts` — All HTTP calls to the backend
- `types/index.ts` — TypeScript interfaces

---

## Important Commands

```bash
# Backend development
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development
cd frontend
npm install
npm run dev

# Tests
cd backend
pytest tests/ -v

# Docker
docker-compose up --build
docker-compose down

# Makefile shortcuts
make install-backend
make install-frontend
make test
make docker-up
make docker-down
```

---

## Coding Conventions

### Backend
- All routes must be thin: validate input, call a service, return a schema.
- Business logic belongs in `services/`, never in `api/`.
- Use Pydantic models for all request/response bodies.
- Use `app.core.config.settings` for all configuration; never hardcode values.
- Use `app.core.logging` for structured logging, not `print()`.
- Return typed responses — never return raw dicts from API routes.
- Raise `HTTPException` with meaningful status codes and messages.
- Handle all external I/O (file reads, model inference) with try/except.

### Frontend
- All API calls must go through `services/api.ts`.
- Use TypeScript interfaces from `types/index.ts`; never use `any`.
- Every async operation needs a loading state and an error state.
- Backend URL comes from `import.meta.env.VITE_API_URL`; never hardcode it.
- Keep components focused and under ~150 lines where possible.

---

## Testing Commands

```bash
# Run all tests
cd backend && pytest tests/ -v

# Run a specific test file
cd backend && pytest tests/test_chunker.py -v

# Run with coverage
cd backend && pytest tests/ --cov=app --cov-report=term-missing
```

Tests must not require paid API keys. Mock or skip any test that would need external calls.
Use real (small) PDF files or generate test PDFs programmatically in fixtures.

---

## Rules for Modifying This Project

1. Do not add business logic to `api/` routes — place it in `services/`.
2. Do not change the chunker without updating `test_chunker.py`.
3. Do not change the API response schemas without updating `types/index.ts` in the frontend.
4. Do not hardcode model names, paths, or API keys anywhere.
5. Do not remove tests unless you are replacing them with better tests.
6. Always update `ARCHITECTURE.md` if the data flow or module responsibilities change.
7. Always update `README.md` if setup steps or API contracts change.
8. Always update `TASKS.md` when completing or adding tasks.
9. Do not add new dependencies without a justification comment in `requirements.txt`.

---

## Security Rules

- Never hardcode API keys or secrets — use `.env` and `pydantic-settings`.
- Never commit `.env` — only `.env.example` is committed.
- Validate all uploaded files: check MIME type, extension, and size.
- Never expose raw stack traces to API clients — use structured error responses.
- Sanitize file paths: always use `os.path.basename()` on uploaded filenames.
- Never use `shell=True` in subprocess calls.
- Never log API keys or user data.

---

## What Claude Must Never Do

- Never invent model performance numbers or benchmark results.
- Never claim the system is production-ready without real testing.
- Never remove the retrieval-only fallback behavior from `generator.py`.
- Never commit `.env` or files with real credentials.
- Never put all logic in `main.py`.
- Never generate answers that go beyond the retrieved context.
- Never fake evaluation metrics.

---

## Definition of Done

A feature is complete when:
1. The service logic is implemented and handles edge cases.
2. The API route is implemented with correct status codes.
3. Pydantic schemas are defined for all inputs and outputs.
4. At least one meaningful test covers the core logic.
5. The README is updated if the feature changes the public interface.
6. The TASKS.md checklist is updated.
