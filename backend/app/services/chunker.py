from typing import Any, Dict, List

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def chunk_pages(
    pages: List[Dict[str, Any]],
    document_id: str,
    filename: str,
    chunk_size: int = settings.CHUNK_SIZE,
    chunk_overlap: int = settings.CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """
    Split page-level text into overlapping character-based chunks.

    Each chunk dict contains:
        chunk_id (str): unique identifier — "{document_id}_p{page}_c{index}"
        document_id (str)
        filename (str)
        page_number (int): source page (1-indexed)
        text (str): chunk content
        character_start (int): start offset within the page text
        character_end (int): end offset within the page text

    Args:
        pages: output of document_loader.extract_text_from_pdf()
        document_id: UUID of the parent document
        filename: original PDF filename (for display in citations)
        chunk_size: max characters per chunk
        chunk_overlap: overlap between consecutive chunks
    """
    if chunk_overlap >= chunk_size:
        raise ValueError(
            f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})."
        )

    chunks: List[Dict[str, Any]] = []
    chunk_index = 0

    for page in pages:
        text: str = page["text"]
        page_number: int = page["page_number"]

        if not text:
            continue

        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk_id = f"{document_id}_p{page_number}_c{chunk_index}"
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "document_id": document_id,
                        "filename": filename,
                        "page_number": page_number,
                        "text": chunk_text,
                        "character_start": start,
                        "character_end": end,
                    }
                )
                chunk_index += 1

            if end >= len(text):
                break

            # Move forward by (chunk_size - overlap) to create the overlapping window
            start = end - chunk_overlap

    logger.info(
        "Chunking complete.",
        document_id=document_id,
        total_chunks=len(chunks),
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return chunks
