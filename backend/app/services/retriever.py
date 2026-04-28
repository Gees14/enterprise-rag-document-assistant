from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store_service

logger = get_logger(__name__)


class RetrieverService:
    """
    Orchestrates query embedding and vector store retrieval.

    Flow:
        1. Embed the natural language query.
        2. Query ChromaDB for top-k most similar chunks.
        3. Apply minimum score filter (optional).
        4. Return structured results.
    """

    def retrieve(
        self,
        question: str,
        top_k: int = settings.DEFAULT_TOP_K,
        min_score: float = settings.MIN_SIMILARITY_SCORE,
        document_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the top-k relevant chunks for a question.

        Returns a list of dicts with keys:
            chunk_id, text, metadata, score
        """
        query_embedding = embedding_service.embed_query(question)
        raw_results = vector_store_service.query(
            query_embedding=query_embedding,
            top_k=top_k,
            document_ids=document_ids,
        )

        # Apply minimum score filter
        if min_score > 0.0:
            raw_results = [r for r in raw_results if r["score"] >= min_score]

        logger.info(
            "Retrieval complete.",
            question_snippet=question[:60],
            top_k=top_k,
            results_returned=len(raw_results),
        )
        return raw_results


retriever_service = RetrieverService()
