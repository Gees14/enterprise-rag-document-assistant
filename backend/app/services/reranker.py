from typing import Any, Dict, List

from app.core.logging import get_logger

logger = get_logger(__name__)


class RerankerService:
    """
    Reranks retrieved chunks by relevance score.

    Current implementation: simple descending-score sort.
    This is a clean extension point for cross-encoder reranking.

    To upgrade to cross-encoder reranking:
        1. pip install sentence-transformers (already installed)
        2. Load cross-encoder/ms-marco-MiniLM-L-6-v2
        3. Score (question, chunk_text) pairs
        4. Replace the sort with cross-encoder scores

    The interface is stable — callers don't need to change.
    """

    def rerank(
        self,
        question: str,
        chunks: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Return chunks sorted by relevance score (descending).

        Args:
            question: the user's original query (available for future cross-encoder use)
            chunks: retrieval results from RetrieverService

        Returns:
            Same chunk dicts, reordered by score.
        """
        reranked = sorted(chunks, key=lambda c: c["score"], reverse=True)
        logger.debug(
            "Reranking complete.",
            strategy="score_sort",
            count=len(reranked),
        )
        return reranked


reranker_service = RerankerService()
