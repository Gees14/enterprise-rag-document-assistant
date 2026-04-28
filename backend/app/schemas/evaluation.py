from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EvalQuestion(BaseModel):
    question: str
    expected_keywords: List[str]
    relevant_document: str
    relevant_pages: List[int]


class PerQuestionResult(BaseModel):
    question: str
    retrieved_documents: List[str]
    retrieved_pages: List[int]
    keyword_hits: List[str]
    keyword_misses: List[str]
    keyword_coverage: float
    reciprocal_rank: float
    top_score: float
    latency_ms: int
    relevant_doc_retrieved: bool


class EvalMetrics(BaseModel):
    precision_at_k: float = Field(..., description="Fraction of top-k results that are relevant")
    recall_at_k: float = Field(..., description="Fraction of relevant results found in top-k")
    mean_reciprocal_rank: float = Field(..., description="Average of 1/rank for first relevant result")
    avg_keyword_coverage: float = Field(..., description="Average keyword coverage across questions")
    avg_latency_ms: float = Field(..., description="Average retrieval latency in milliseconds")
    total_questions: int
    questions_with_relevant_doc: int


class EvalRecommendation(BaseModel):
    metric: str
    value: float
    recommendation: str


class EvalRunResponse(BaseModel):
    metrics: EvalMetrics
    per_question_results: List[PerQuestionResult]
    recommendations: List[EvalRecommendation]
    eval_timestamp: str
