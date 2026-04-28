# PROJECT_SPEC.md — Enterprise RAG Document Assistant

## Product Goal

Build a production-quality Retrieval-Augmented Generation (RAG) system that enables knowledge workers to upload their PDF documents and ask natural language questions, receiving accurate, grounded answers with citations to specific document sections.

The system must work fully offline (retrieval-only mode) and optionally leverage an OpenAI-compatible LLM when an API key is provided.

---

## Target Users

- **AI/ML Engineers** evaluating RAG pipeline architectures
- **Knowledge Workers** who need to query large document repositories
- **Developers** looking for a reference implementation of a production RAG system
- **Hiring managers / technical interviewers** reviewing portfolio projects

---

## User Stories

### Document Management
- As a user, I can upload one or more PDF files so I can query their content.
- As a user, I can see a list of all uploaded documents and their indexing status.
- As a user, I can trigger re-indexing of a document if needed.
- As a user, I can delete a document and its associated vector data.
- As a user, I am prevented from uploading non-PDF files.
- As a user, I see clear feedback when a document has been successfully indexed.

### Question Answering
- As a user, I can type a natural language question and receive an answer grounded in my documents.
- As a user, I can see which document chunks were used to generate the answer.
- As a user, I can see the page number and a text snippet for each cited source.
- As a user, I receive a clear message when the documents do not contain enough information to answer my question.
- As a user, the system works even without an LLM API key (retrieval-only mode).

### Evaluation
- As a developer, I can run a RAG evaluation against a set of predefined questions.
- As a developer, I can see precision@k, recall@k, MRR, and keyword coverage metrics.
- As a developer, I can see per-question retrieval results to diagnose failures.
- As a developer, I receive actionable recommendations based on evaluation results.

---

## Core Features

| Feature | Priority | Status |
|---|---|---|
| PDF upload and validation | P0 | Implemented |
| Text extraction (pdfplumber) | P0 | Implemented |
| Overlapping text chunking | P0 | Implemented |
| sentence-transformers embeddings | P0 | Implemented |
| ChromaDB vector indexing | P0 | Implemented |
| Semantic retrieval (top-k) | P0 | Implemented |
| Retrieval-only response mode | P0 | Implemented |
| LLM generation (OpenAI-compatible) | P1 | Implemented |
| Source citations in responses | P1 | Implemented |
| Simple score-based reranking | P1 | Implemented |
| RAG evaluation metrics | P1 | Implemented |
| React dashboard frontend | P1 | Implemented |
| Document management UI | P1 | Implemented |
| Evaluation dashboard UI | P2 | Implemented |
| Docker + docker-compose | P2 | Implemented |
| GitHub Actions CI | P2 | Implemented |

---

## Non-Functional Requirements

### Performance
- Document indexing (< 50 pages) should complete in under 30 seconds on a modern laptop.
- Query response (retrieval-only) should return within 2 seconds.
- Query response (with LLM) depends on API latency but should return within 10 seconds.

### Reliability
- The system must return a valid response for all queries, even when context is insufficient.
- File uploads must be validated and rejected gracefully for unsupported types.
- All services must handle exceptions without crashing the server.

### Scalability (portfolio scope)
- Designed for single-user local use.
- ChromaDB supports up to millions of vectors; scaling to multi-user would require a proper database for metadata and a hosted vector store.

### Security
- File uploads validated by extension and MIME type.
- No secrets in source code.
- File path sanitization prevents directory traversal.
- Internal errors never exposed to API clients.

---

## API Requirements

### Documents API
```
POST   /documents/upload          Upload one or more PDF files
GET    /documents                 List all documents
DELETE /documents/{document_id}   Delete a document and its vectors
POST   /documents/{document_id}/index   Index (or re-index) a document
```

### Chat API
```
POST   /chat/query    Ask a question, receive an answer with sources
```

### Evaluation API
```
POST   /eval/run      Run RAG evaluation against questions.json
GET    /eval/results  Get the latest evaluation results
```

### Health API
```
GET    /health        System health check
GET    /health/ready  Readiness check (vector store reachable)
```

---

## Success Criteria

1. A user can upload a PDF and ask a question about it in under 5 minutes from a fresh start.
2. Retrieval works without any API keys.
3. All pytest tests pass.
4. The evaluation suite returns meaningful metrics.
5. The system runs fully in Docker with `docker-compose up`.
6. The README explains the architecture clearly and accurately.

---

## Out-of-Scope Features

- Multi-user authentication and authorization
- Hosted vector database (Pinecone, Weaviate, etc.)
- Real-time streaming of LLM responses
- Document versioning
- Non-PDF file formats (Word, HTML, etc.)
- Fine-tuning or training any model
- Production deployment (Kubernetes, cloud infra)
- Multi-tenancy
- Document access controls

---

## Known Limitations

1. **Embedding model cold start**: The sentence-transformers model is loaded on first query, adding ~5s to the initial request.
2. **No persistent document metadata DB**: Document metadata is stored in a JSON file; concurrent writes are not safe.
3. **Retrieval quality depends on chunk size**: Very large or small chunks affect retrieval quality significantly.
4. **LLM hallucination risk**: When using an LLM, responses may still occasionally go beyond retrieved context; the system prompts strongly against this.
5. **PDF text quality**: Scanned PDFs without OCR will extract empty text. Only text-based PDFs are supported.
