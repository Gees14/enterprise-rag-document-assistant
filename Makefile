.PHONY: help install-backend install-frontend test test-verbose \
        run-backend run-frontend docker-up docker-down docker-build clean lint

PYTHON  := python
PIP     := pip
NPM     := npm
BACKEND := backend
FRONTEND := frontend

# ─────────────────────────────────────────────
help:
	@echo ""
	@echo "  Enterprise RAG Document Assistant"
	@echo ""
	@echo "  install-backend     Install Python dependencies"
	@echo "  install-frontend    Install Node dependencies"
	@echo "  run-backend         Start FastAPI dev server on :8000"
	@echo "  run-frontend        Start Vite dev server on :5173"
	@echo "  test                Run all pytest tests"
	@echo "  test-verbose        Run tests with verbose output"
	@echo "  docker-build        Build Docker images"
	@echo "  docker-up           Start all services with Docker Compose"
	@echo "  docker-down         Stop all services"
	@echo "  clean               Remove temp files, caches, build artifacts"
	@echo "  lint                Run linters"
	@echo ""

# ─────────────────────────────────────────────
install-backend:
	cd $(BACKEND) && $(PIP) install -r requirements.txt

install-frontend:
	cd $(FRONTEND) && $(NPM) install

# ─────────────────────────────────────────────
run-backend:
	cd $(BACKEND) && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd $(FRONTEND) && $(NPM) run dev

# ─────────────────────────────────────────────
test:
	cd $(BACKEND) && pytest tests/ -q

test-verbose:
	cd $(BACKEND) && pytest tests/ -v --tb=short

test-coverage:
	cd $(BACKEND) && pytest tests/ --cov=app --cov-report=term-missing

# ─────────────────────────────────────────────
docker-build:
	docker-compose build

docker-up:
	docker-compose up --build -d
	@echo ""
	@echo "  Frontend: http://localhost:5173"
	@echo "  Backend:  http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"
	@echo ""

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# ─────────────────────────────────────────────
lint:
	cd $(BACKEND) && python -m py_compile app/**/*.py
	cd $(FRONTEND) && $(NPM) run lint || true

# ─────────────────────────────────────────────
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf $(FRONTEND)/dist $(FRONTEND)/node_modules/.cache 2>/dev/null || true
	@echo "Cleaned."
