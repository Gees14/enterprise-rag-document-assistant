from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class SourceReference(BaseModel):
    document_name: str
    page_number: int
    chunk_id: str
    snippet: str
    score: float


class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    page_number: int
    text: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    sources: List[SourceReference]
    retrieved_chunks: List[RetrievedChunk]
    latency_ms: int
    mode: str = Field(
        default="retrieval_only",
        description="'retrieval_only' or 'llm_generated'",
    )
