import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, documents, evaluation, health
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging, get_logger

# Configure logging before anything else
configure_logging()
logger = get_logger(__name__)

# Ensure data directories exist
for path in [settings.UPLOAD_DIR, settings.VECTOR_STORE_DIR, settings.EVAL_DIR]:
    os.makedirs(path, exist_ok=True)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Production-quality RAG system: upload PDFs, index them into a vector database, "
            "and ask natural language questions with grounded answers and citations."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS — allows the React frontend to call the API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global exception handlers
    register_error_handlers(app)

    # Routers
    app.include_router(health.router)
    app.include_router(documents.router)
    app.include_router(chat.router)
    app.include_router(evaluation.router)

    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info(
            "Application started.",
            app=settings.APP_NAME,
            version=settings.APP_VERSION,
            llm_enabled=settings.llm_enabled,
            embedding_model=settings.EMBEDDING_MODEL,
        )

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        logger.info("Application shutting down.")

    return app


app = create_app()
