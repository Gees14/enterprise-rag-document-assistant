from unittest.mock import MagicMock, patch

import pytest


def _make_chunk(chunk_id: str, text: str, score: float, page: int = 1) -> dict:
    return {
        "chunk_id": chunk_id,
        "text": text,
        "score": score,
        "metadata": {
            "document_id": "doc-001",
            "filename": "test.pdf",
            "page_number": page,
            "character_start": 0,
            "character_end": len(text),
        },
    }


@patch("app.services.retriever.vector_store_service")
@patch("app.services.retriever.embedding_service")
def test_retrieve_returns_chunks(mock_embed, mock_vs):
    from app.services.retriever import RetrieverService

    mock_embed.embed_query.return_value = [0.1] * 384
    mock_vs.query.return_value = [
        _make_chunk("chunk-001", "Machine learning is a subset of AI.", 0.92),
        _make_chunk("chunk-002", "Neural networks mimic the human brain.", 0.85),
    ]

    svc = RetrieverService()
    results = svc.retrieve("What is machine learning?", top_k=5)

    assert len(results) == 2
    mock_embed.embed_query.assert_called_once()
    mock_vs.query.assert_called_once()


@patch("app.services.retriever.vector_store_service")
@patch("app.services.retriever.embedding_service")
def test_retrieve_applies_min_score_filter(mock_embed, mock_vs):
    from app.services.retriever import RetrieverService

    mock_embed.embed_query.return_value = [0.1] * 384
    mock_vs.query.return_value = [
        _make_chunk("chunk-001", "High relevance content.", 0.90),
        _make_chunk("chunk-002", "Low relevance content.", 0.15),
    ]

    svc = RetrieverService()
    results = svc.retrieve("Some question?", top_k=5, min_score=0.5)

    assert len(results) == 1
    assert results[0]["chunk_id"] == "chunk-001"


@patch("app.services.retriever.vector_store_service")
@patch("app.services.retriever.embedding_service")
def test_retrieve_empty_store_returns_empty(mock_embed, mock_vs):
    from app.services.retriever import RetrieverService

    mock_embed.embed_query.return_value = [0.1] * 384
    mock_vs.query.return_value = []

    svc = RetrieverService()
    results = svc.retrieve("Any question?", top_k=5)
    assert results == []


def test_reranker_sorts_by_score():
    from app.services.reranker import RerankerService

    chunks = [
        _make_chunk("c1", "Third place content.", 0.60),
        _make_chunk("c2", "First place content.", 0.95),
        _make_chunk("c3", "Second place content.", 0.80),
    ]

    svc = RerankerService()
    reranked = svc.rerank("question", chunks)

    assert reranked[0]["chunk_id"] == "c2"
    assert reranked[1]["chunk_id"] == "c3"
    assert reranked[2]["chunk_id"] == "c1"


def test_reranker_empty_input():
    from app.services.reranker import RerankerService

    svc = RerankerService()
    result = svc.rerank("question", [])
    assert result == []
