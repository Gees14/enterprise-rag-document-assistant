from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────
# Custom exceptions
# ─────────────────────────────────────────────


class AppError(Exception):
    """Base class for all application errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DocumentNotFoundError(AppError):
    def __init__(self, document_id: str):
        super().__init__(f"Document '{document_id}' not found.", status_code=404)


class DocumentAlreadyIndexedError(AppError):
    def __init__(self, document_id: str):
        super().__init__(
            f"Document '{document_id}' is already indexed. "
            "Delete and re-upload to re-index.",
            status_code=409,
        )


class InvalidFileTypeError(AppError):
    def __init__(self, filename: str):
        super().__init__(
            f"File '{filename}' is not supported. Only PDF files are accepted.",
            status_code=422,
        )


class FileTooLargeError(AppError):
    def __init__(self, filename: str, max_mb: int):
        super().__init__(
            f"File '{filename}' exceeds the maximum allowed size of {max_mb} MB.",
            status_code=413,
        )


class ExtractionError(AppError):
    def __init__(self, filename: str, detail: str):
        super().__init__(
            f"Could not extract text from '{filename}': {detail}",
            status_code=422,
        )


class VectorStoreError(AppError):
    def __init__(self, detail: str):
        super().__init__(f"Vector store error: {detail}", status_code=500)


class EmbeddingError(AppError):
    def __init__(self, detail: str):
        super().__init__(f"Embedding generation failed: {detail}", status_code=500)


class NoDocumentsIndexedError(AppError):
    def __init__(self):
        super().__init__(
            "No documents have been indexed yet. "
            "Upload and index a PDF before querying.",
            status_code=400,
        )


# ─────────────────────────────────────────────
# Global exception handlers
# ─────────────────────────────────────────────


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "Application error",
            path=str(request.url.path),
            status_code=exc.status_code,
            message=exc.message,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "type": type(exc).__name__},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "Unhandled exception",
            path=str(request.url.path),
            exc_info=exc,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "An unexpected error occurred. Please try again.",
                "type": "InternalServerError",
            },
        )
