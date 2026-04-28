from typing import List, Dict, Any

import pdfplumber

from app.core.errors import ExtractionError
from app.core.logging import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract text from a PDF file, returning a list of page-level dicts.

    Each dict contains:
        page_number (int): 1-indexed page number
        text (str): extracted plain text (empty string for blank/image pages)

    Raises ExtractionError for corrupted or unreadable files.
    """
    pages: List[Dict[str, Any]] = []

    try:
        with pdfplumber.open(file_path) as pdf:
            if len(pdf.pages) == 0:
                raise ExtractionError(file_path, "PDF has no pages.")

            for i, page in enumerate(pdf.pages, start=1):
                try:
                    raw_text = page.extract_text()
                    text = raw_text.strip() if raw_text else ""
                except Exception as page_err:
                    logger.warning(
                        "Failed to extract text from page; skipping.",
                        file=file_path,
                        page=i,
                        error=str(page_err),
                    )
                    text = ""

                pages.append({"page_number": i, "text": text})

    except ExtractionError:
        raise
    except Exception as e:
        logger.error("PDF extraction failed.", file=file_path, error=str(e))
        raise ExtractionError(file_path, str(e))

    non_empty = sum(1 for p in pages if p["text"])
    logger.info(
        "PDF extraction complete.",
        file=file_path,
        total_pages=len(pages),
        non_empty_pages=non_empty,
    )
    return pages
