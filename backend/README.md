# Backend — Enterprise RAG Document Assistant

FastAPI backend for the RAG system.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp ../.env.example .env

# Create data directories
mkdir -p data/uploads data/vector_store data/eval

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

## Project Structure

```
backend/
├── app/
│   ├── main.py            # FastAPI app factory
│   ├── api/               # Route handlers (thin)
│   ├── core/              # Config, logging, error handling
│   ├── schemas/           # Pydantic request/response models
│   ├── models/            # Domain models + document repository
│   └── services/          # All business logic
├── data/
│   ├── uploads/           # Uploaded PDFs (git-ignored)
│   ├── vector_store/      # ChromaDB persistence (git-ignored)
│   └── eval/
│       └── questions.json # Evaluation question set
└── tests/
```

## Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=app --cov-report=term-missing
```

## Key Environment Variables

| Variable | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | sentence-transformers model |
| `CHUNK_SIZE` | `512` | Characters per chunk |
| `CHUNK_OVERLAP` | `64` | Overlap between chunks |
| `OPENAI_API_KEY` | _(empty)_ | Optional: enables LLM generation |
| `LLM_MODEL` | `gpt-4o-mini` | OpenAI-compatible model name |
| `DEFAULT_TOP_K` | `5` | Default retrieval count |
