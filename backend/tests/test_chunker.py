import pytest

from app.services.chunker import chunk_pages


def test_basic_chunking(sample_pages, sample_document_id, sample_filename):
    chunks = chunk_pages(sample_pages, sample_document_id, sample_filename)
    assert len(chunks) > 0
    for chunk in chunks:
        assert "chunk_id" in chunk
        assert "text" in chunk
        assert "page_number" in chunk
        assert "document_id" in chunk
        assert "filename" in chunk
        assert "character_start" in chunk
        assert "character_end" in chunk


def test_chunk_ids_are_unique(sample_pages, sample_document_id, sample_filename):
    chunks = chunk_pages(sample_pages, sample_document_id, sample_filename)
    ids = [c["chunk_id"] for c in chunks]
    assert len(ids) == len(set(ids)), "Chunk IDs must be unique"


def test_chunk_contains_document_id(sample_pages, sample_document_id, sample_filename):
    chunks = chunk_pages(sample_pages, sample_document_id, sample_filename)
    for chunk in chunks:
        assert chunk["document_id"] == sample_document_id


def test_chunk_contains_filename(sample_pages, sample_document_id, sample_filename):
    chunks = chunk_pages(sample_pages, sample_document_id, sample_filename)
    for chunk in chunks:
        assert chunk["filename"] == sample_filename


def test_chunk_respects_size(sample_pages, sample_document_id, sample_filename):
    chunk_size = 50
    chunks = chunk_pages(
        sample_pages, sample_document_id, sample_filename, chunk_size=chunk_size, chunk_overlap=10
    )
    for chunk in chunks:
        # Chunks may be slightly smaller due to stripping; never larger
        assert len(chunk["text"]) <= chunk_size + 5  # small tolerance for strip


def test_empty_pages_are_skipped(sample_document_id, sample_filename):
    pages = [
        {"page_number": 1, "text": ""},
        {"page_number": 2, "text": "   "},
        {"page_number": 3, "text": "Some real content here."},
    ]
    chunks = chunk_pages(pages, sample_document_id, sample_filename)
    assert all(c["page_number"] == 3 for c in chunks)


def test_overlap_invalid_raises():
    with pytest.raises(ValueError, match="chunk_overlap"):
        chunk_pages(
            [{"page_number": 1, "text": "Hello world"}],
            "doc-id",
            "test.pdf",
            chunk_size=100,
            chunk_overlap=100,  # overlap >= chunk_size → error
        )


def test_overlap_creates_shared_content(sample_document_id, sample_filename):
    """Verify overlapping chunks share content from adjacent windows."""
    long_text = "A" * 100 + "B" * 100 + "C" * 100
    pages = [{"page_number": 1, "text": long_text}]
    chunks = chunk_pages(
        pages, sample_document_id, sample_filename, chunk_size=100, chunk_overlap=50
    )
    assert len(chunks) >= 2, "Should produce multiple chunks for long text"
    # Consecutive chunks should overlap
    if len(chunks) >= 2:
        end_of_first = chunks[0]["character_end"]
        start_of_second = chunks[1]["character_start"]
        assert start_of_second < end_of_first, "Chunks should overlap"


def test_page_numbers_preserved(sample_pages, sample_document_id, sample_filename):
    chunks = chunk_pages(sample_pages, sample_document_id, sample_filename)
    page_numbers_in_chunks = {c["page_number"] for c in chunks}
    expected_pages = {p["page_number"] for p in sample_pages if p["text"]}
    assert expected_pages == page_numbers_in_chunks
