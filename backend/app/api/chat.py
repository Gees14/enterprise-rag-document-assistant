import time

from fastapi import APIRouter

from app.core.errors import NoDocumentsIndexedError
from app.core.logging import get_logger
from app.schemas.chat import ChatRequest, ChatResponse, RetrievedChunk, SourceReference
from app.services.generator import generator_service
from app.services.reranker import reranker_service
from app.services.retriever import retriever_service
from app.services.vector_store import vector_store_service

router = APIRouter(prefix="/chat", tags=["chat"])
logger = get_logger(__name__)


@router.post("/query", response_model=ChatResponse)
async def query(request: ChatRequest) -> ChatResponse:
    """
    Accept a natural language question and return a grounded answer with citations.

    If no LLM API key is configured, the system returns the top retrieved chunks
    as the answer (retrieval-only mode). This mode requires no external API keys.
    """
    t0 = time.perf_counter()

    if vector_store_service.count() == 0:
        raise NoDocumentsIndexedError()

    raw_chunks = retriever_service.retrieve(
        question=request.question,
        top_k=request.top_k,
    )
    reranked_chunks = reranker_service.rerank(request.question, raw_chunks)

    answer, confidence, mode = generator_service.generate(
        question=request.question,
        chunks=reranked_chunks,
    )

    latency_ms = int((time.perf_counter() - t0) * 1000)

    sources = [
        SourceReference(
            document_name=c["metadata"].get("filename", "Unknown"),
            page_number=c["metadata"].get("page_number", 0),
            chunk_id=c["chunk_id"],
            snippet=c["text"][:300] + ("..." if len(c["text"]) > 300 else ""),
            score=c["score"],
        )
        for c in reranked_chunks
    ]

    retrieved = [
        RetrievedChunk(
            chunk_id=c["chunk_id"],
            document_id=c["metadata"].get("document_id", ""),
            filename=c["metadata"].get("filename", ""),
            page_number=c["metadata"].get("page_number", 0),
            text=c["text"],
            score=c["score"],
        )
        for c in reranked_chunks
    ]

    logger.info(
        "Query complete.",
        question_snippet=request.question[:60],
        mode=mode,
        latency_ms=latency_ms,
        sources=len(sources),
    )

    return ChatResponse(
        answer=answer,
        confidence=confidence,
        sources=sources,
        retrieved_chunks=retrieved,
        latency_ms=latency_ms,
        mode=mode,
    )
