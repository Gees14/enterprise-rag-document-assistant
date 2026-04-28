import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.evaluation import (
    EvalMetrics,
    EvalQuestion,
    EvalRecommendation,
    EvalRunResponse,
    PerQuestionResult,
)
from app.services.retriever import retriever_service

logger = get_logger(__name__)


def load_eval_questions() -> List[EvalQuestion]:
    """Load evaluation questions from data/eval/questions.json."""
    path = os.path.join(settings.EVAL_DIR, "questions.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [EvalQuestion(**q) for q in raw]


def run_evaluation(top_k: int = 5) -> EvalRunResponse:
    """
    Run RAG evaluation metrics against the predefined question set.

    Metrics computed:
        - precision@k: fraction of top-k retrieved chunks from the relevant document
        - recall@k: fraction of relevant pages found in top-k (capped at 1.0)
        - mean reciprocal rank (MRR): 1/rank of the first relevant result
        - avg keyword coverage: fraction of expected keywords found in retrieved text
        - avg retrieval latency (ms)
    """
    questions = load_eval_questions()
    if not questions:
        raise ValueError("No evaluation questions found. Check data/eval/questions.json.")

    per_question: List[PerQuestionResult] = []
    all_latencies: List[float] = []
    all_mrr: List[float] = []
    all_precision: List[float] = []
    all_recall: List[float] = []
    all_keyword_coverage: List[float] = []
    questions_with_relevant_doc = 0

    for q in questions:
        t0 = time.perf_counter()
        try:
            chunks = retriever_service.retrieve(q.question, top_k=top_k)
        except Exception as e:
            logger.warning("Retrieval failed for eval question.", question=q.question, error=str(e))
            chunks = []
        latency_ms = int((time.perf_counter() - t0) * 1000)
        all_latencies.append(latency_ms)

        retrieved_docs = [c["metadata"].get("filename", "") for c in chunks]
        retrieved_pages = [c["metadata"].get("page_number", 0) for c in chunks]

        # Check if the relevant document was retrieved at any rank
        relevant_mask = [doc == q.relevant_document for doc in retrieved_docs]
        relevant_doc_retrieved = any(relevant_mask)
        if relevant_doc_retrieved:
            questions_with_relevant_doc += 1

        # Precision@k: fraction of retrieved chunks from the relevant document
        precision = sum(relevant_mask) / top_k if chunks else 0.0
        all_precision.append(precision)

        # Recall@k: fraction of relevant pages found in the top-k pages
        relevant_pages_set = set(q.relevant_pages)
        if relevant_pages_set:
            found_pages = relevant_pages_set.intersection(
                set(p for doc, p in zip(retrieved_docs, retrieved_pages) if doc == q.relevant_document)
            )
            recall = len(found_pages) / len(relevant_pages_set)
        else:
            recall = 1.0
        all_recall.append(recall)

        # MRR: 1/rank of the first relevant result
        rr = 0.0
        for rank, is_relevant in enumerate(relevant_mask, start=1):
            if is_relevant:
                rr = 1.0 / rank
                break
        all_mrr.append(rr)

        # Keyword coverage: fraction of expected keywords found in all retrieved text
        combined_text = " ".join(c["text"].lower() for c in chunks)
        hits = [kw for kw in q.expected_keywords if kw.lower() in combined_text]
        misses = [kw for kw in q.expected_keywords if kw.lower() not in combined_text]
        coverage = len(hits) / len(q.expected_keywords) if q.expected_keywords else 1.0
        all_keyword_coverage.append(coverage)

        top_score = chunks[0]["score"] if chunks else 0.0

        per_question.append(
            PerQuestionResult(
                question=q.question,
                retrieved_documents=retrieved_docs,
                retrieved_pages=retrieved_pages,
                keyword_hits=hits,
                keyword_misses=misses,
                keyword_coverage=round(coverage, 4),
                reciprocal_rank=round(rr, 4),
                top_score=round(top_score, 4),
                latency_ms=latency_ms,
                relevant_doc_retrieved=relevant_doc_retrieved,
            )
        )

    n = len(questions)
    avg = lambda lst: round(sum(lst) / len(lst), 4) if lst else 0.0

    metrics = EvalMetrics(
        precision_at_k=avg(all_precision),
        recall_at_k=avg(all_recall),
        mean_reciprocal_rank=avg(all_mrr),
        avg_keyword_coverage=avg(all_keyword_coverage),
        avg_latency_ms=round(sum(all_latencies) / n, 1),
        total_questions=n,
        questions_with_relevant_doc=questions_with_relevant_doc,
    )

    recommendations = _generate_recommendations(metrics)

    return EvalRunResponse(
        metrics=metrics,
        per_question_results=per_question,
        recommendations=recommendations,
        eval_timestamp=datetime.now(timezone.utc).isoformat(),
    )


def _generate_recommendations(metrics: EvalMetrics) -> List[EvalRecommendation]:
    recs: List[EvalRecommendation] = []

    if metrics.precision_at_k < 0.4:
        recs.append(EvalRecommendation(
            metric="precision_at_k",
            value=metrics.precision_at_k,
            recommendation=(
                "Low precision: many retrieved chunks are from irrelevant documents. "
                "Try reducing CHUNK_SIZE, increasing CHUNK_OVERLAP, or upgrading the embedding model."
            ),
        ))

    if metrics.recall_at_k < 0.6:
        recs.append(EvalRecommendation(
            metric="recall_at_k",
            value=metrics.recall_at_k,
            recommendation=(
                "Low recall: relevant pages are not consistently retrieved. "
                "Try increasing DEFAULT_TOP_K or using a larger embedding model."
            ),
        ))

    if metrics.mean_reciprocal_rank < 0.5:
        recs.append(EvalRecommendation(
            metric="mean_reciprocal_rank",
            value=metrics.mean_reciprocal_rank,
            recommendation=(
                "Low MRR: the most relevant result is rarely ranked first. "
                "Consider adding cross-encoder reranking."
            ),
        ))

    if metrics.avg_keyword_coverage < 0.7:
        recs.append(EvalRecommendation(
            metric="avg_keyword_coverage",
            value=metrics.avg_keyword_coverage,
            recommendation=(
                "Low keyword coverage: expected terms are missing from retrieved chunks. "
                "Try smaller chunk sizes or increase top_k."
            ),
        ))

    if metrics.avg_latency_ms > 2000:
        recs.append(EvalRecommendation(
            metric="avg_latency_ms",
            value=metrics.avg_latency_ms,
            recommendation=(
                "High retrieval latency. Consider pre-warming the embedding model "
                "on startup or using a GPU-accelerated embedding service."
            ),
        ))

    if not recs:
        recs.append(EvalRecommendation(
            metric="overall",
            value=1.0,
            recommendation="All metrics are within acceptable ranges. Good retrieval quality.",
        ))

    return recs
