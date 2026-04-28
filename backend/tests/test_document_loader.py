import os
import tempfile

import pytest

from app.core.errors import ExtractionError


def _create_simple_pdf(text: str = "Hello, this is a test PDF.") -> str:
    """Create a minimal valid PDF in a temp file and return its path."""
    try:
        import fpdf  # type: ignore

        pdf = fpdf.FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=text, ln=True)
        path = tempfile.mktemp(suffix=".pdf")
        pdf.output(path)
        return path
    except ImportError:
        pass

    # Fallback: write a minimal hand-crafted PDF
    # This is a valid 1-page PDF with "Hello World" text
    minimal_pdf = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT /F1 12 Tf 100 700 Td (Hello World) Tj ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000266 00000 n
0000000360 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
441
%%EOF"""
    path = tempfile.mktemp(suffix=".pdf")
    with open(path, "wb") as f:
        f.write(minimal_pdf)
    return path


def test_extract_returns_list_of_pages():
    from app.services.document_loader import extract_text_from_pdf

    path = _create_simple_pdf()
    try:
        pages = extract_text_from_pdf(path)
        assert isinstance(pages, list)
        assert len(pages) >= 1
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_extract_page_has_required_keys():
    from app.services.document_loader import extract_text_from_pdf

    path = _create_simple_pdf()
    try:
        pages = extract_text_from_pdf(path)
        for page in pages:
            assert "page_number" in page
            assert "text" in page
            assert isinstance(page["page_number"], int)
            assert isinstance(page["text"], str)
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_extract_page_numbers_are_1_indexed():
    from app.services.document_loader import extract_text_from_pdf

    path = _create_simple_pdf()
    try:
        pages = extract_text_from_pdf(path)
        assert pages[0]["page_number"] == 1
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_extract_invalid_file_raises_error():
    from app.services.document_loader import extract_text_from_pdf

    path = tempfile.mktemp(suffix=".pdf")
    with open(path, "wb") as f:
        f.write(b"this is not a pdf file at all")
    try:
        with pytest.raises(ExtractionError):
            extract_text_from_pdf(path)
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_extract_nonexistent_file_raises_error():
    from app.services.document_loader import extract_text_from_pdf

    with pytest.raises(ExtractionError):
        extract_text_from_pdf("/nonexistent/path/to/file.pdf")
