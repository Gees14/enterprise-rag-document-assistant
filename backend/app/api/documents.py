import os
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.errors import (
    DocumentNotFoundError,
    ExtractionError,
    FileTooLargeError,
    InvalidFileTypeError,
)
from app.core.logging import get_logger
from app.models.domain import Document, DocumentStatus, document_repository
from app.schemas.document import (
    DeleteResponse,
    DocumentListResponse,
    DocumentResponse,
    IndexResponse,
    UploadResponse,
)
from app.services.chunker import chunk_pages
from app.services.document_loader import extract_text_from_pdf
from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store_service

router = APIRouter(prefix="/documents", tags=["documents"])
logger = get_logger(__name__)

MAX_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


def _validate_file(file: UploadFile, content: bytes) -> None:
    """Validate file extension and size. Raises on failure."""
    filename = os.path.basename(file.filename or "")
    _, ext = os.path.splitext(filename.lower())
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise InvalidFileTypeError(filename)
    if len(content) > MAX_BYTES:
        raise FileTooLargeError(filename, settings.MAX_FILE_SIZE_MB)


def _safe_filename(name: str) -> str:
    """Strip directory components to prevent path traversal."""
    return os.path.basename(name or "upload.pdf")


@router.post("/upload", response_model=List[UploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_documents(files: List[UploadFile] = File(...)) -> List[UploadResponse]:
    """Upload one or more PDF files."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    responses: List[UploadResponse] = []

    for file in files:
        content = await file.read()
        _validate_file(file, content)

        doc = Document(
            filename=_safe_filename(file.filename),
            file_path="",
            file_size_bytes=len(content),
        )
        save_path = os.path.join(settings.UPLOAD_DIR, f"{doc.id}.pdf")
        doc.file_path = save_path

        with open(save_path, "wb") as f:
            f.write(content)

        document_repository.save(doc)
        logger.info("Document uploaded.", document_id=doc.id, filename=doc.filename)

        responses.append(
            UploadResponse(
                document_id=doc.id,
                filename=doc.filename,
                status=doc.status,
                file_size_bytes=doc.file_size_bytes,
                message="Upload successful. Call /index to embed and index this document.",
            )
        )

    return responses


@router.get("", response_model=DocumentListResponse)
async def list_documents() -> DocumentListResponse:
    """Return all uploaded documents with their indexing status."""
    docs = document_repository.list_all()
    return DocumentListResponse(
        documents=[DocumentResponse(**d.model_dump()) for d in docs],
        total=len(docs),
    )


@router.delete("/{document_id}", response_model=DeleteResponse)
async def delete_document(document_id: str) -> DeleteResponse:
    """Delete a document, its file, and all its vector store chunks."""
    doc = document_repository.get(document_id)
    if not doc:
        raise DocumentNotFoundError(document_id)

    # Remove from vector store
    vector_store_service.delete_by_document_id(document_id)

    # Remove file from disk
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    document_repository.delete(document_id)
    logger.info("Document deleted.", document_id=document_id)

    return DeleteResponse(
        document_id=document_id,
        message=f"Document '{doc.filename}' and all associated data have been deleted.",
    )


@router.post("/{document_id}/index", response_model=IndexResponse)
async def index_document(document_id: str) -> IndexResponse:
    """Extract text, chunk, embed, and index a previously uploaded document."""
    doc = document_repository.get(document_id)
    if not doc:
        raise DocumentNotFoundError(document_id)

    if doc.status == DocumentStatus.INDEXED:
        # Allow re-indexing by clearing existing chunks first
        vector_store_service.delete_by_document_id(document_id)
        logger.info("Re-indexing: cleared existing chunks.", document_id=document_id)

    document_repository.update_status(document_id, DocumentStatus.INDEXING)

    try:
        pages = extract_text_from_pdf(doc.file_path)
        chunks = chunk_pages(pages, document_id, doc.filename)

        if not chunks:
            document_repository.update_status(document_id, DocumentStatus.FAILED)
            raise HTTPException(
                status_code=422,
                detail="No text could be extracted from this PDF. "
                "Ensure it is a text-based PDF (not scanned/image-only).",
            )

        texts = [c["text"] for c in chunks]
        embeddings = embedding_service.embed_texts(texts)
        vector_store_service.add_chunks(chunks, embeddings)

        document_repository.update_status(
            document_id,
            DocumentStatus.INDEXED,
            chunk_count=len(chunks),
            page_count=len(pages),
        )

        logger.info(
            "Document indexed.",
            document_id=document_id,
            chunks=len(chunks),
            pages=len(pages),
        )

        return IndexResponse(
            document_id=document_id,
            filename=doc.filename,
            status=DocumentStatus.INDEXED,
            chunk_count=len(chunks),
            page_count=len(pages),
            message=f"Successfully indexed {len(chunks)} chunks across {len(pages)} pages.",
        )

    except (ExtractionError, HTTPException):
        raise
    except Exception as e:
        document_repository.update_status(document_id, DocumentStatus.FAILED)
        logger.error("Indexing failed.", document_id=document_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}")
