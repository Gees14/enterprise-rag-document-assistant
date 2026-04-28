import json
import os
import tempfile
from unittest.mock import patch

import pytest

from app.schemas.evaluation import EvalQuestion


def _write_questions(path: str, questions: list) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(questions, f)


SAMPLE_QUESTIONS = [
    {
        "question": "What is machine learning?",
        "expected_keywords": ["machine", "learning", "artificial"],
        "relevant_document": "ml_intro.pdf",
        "relevant_pages": [1],
    },
    {
        "question": "What are neural networks?",
        "expected_keywords": ["neural", "network", "brain"],
        "relevant_document": "ml_intro.pdf",
        "relevant_pages": [2],
    },
]

MOCK_CHUNKS = [
    {
        "chunk_id": "ml_intro.pdf_p1_c0",
        "text": "Machine learning is a subset of artificial intelligence.",
        "score": 0.92,
        "metadata": {
            "document_id": "doc-001",
            "filename": "ml_intro.pdf",
            "page_number": 1,
            "character_start": 0,
            "character_end": 55,
        },
    }
]


def test_load_eval_questions_returns_list():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "questions.json")
        _write_questions(path, SAMPLE_QUESTIONS)

        with patch("app.services.evaluator.settings") as mock_settings:
            mock_settings.EVAL_DIR = tmpdir

            from app.services.evaluator import load_eval_questions

            questions = load_eval_questions()
            assert len(questions) == 2
            assert all(isinstance(q, EvalQuestion) for q in questions)


def test_load_eval_questions_empty_when_file_missing():
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("app.services.evaluator.settings") as mock_settings:
            mock_settings.EVAL_DIR = tmpdir

            from app.services.evaluator import load_eval_questions

            questions = load_eval_questions()
            assert questions == []


def test_run_evaluation_raises_when_no_questions():
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("app.services.evaluator.settings") as mock_settings:
            mock_settings.EVAL_DIR = tmpdir

            from app.services.evaluator import run_evaluation

            with pytest.raises(ValueError, match="No evaluation questions"):
                run_evaluation()


@patch("app.services.evaluator.retriever_service")
def test_run_evaluation_computes_metrics(mock_retriever):
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "questions.json")
        _write_questions(path, SAMPLE_QUESTIONS)

        mock_retriever.retrieve.return_value = MOCK_CHUNKS

        with patch("app.services.evaluator.settings") as mock_settings:
            mock_settings.EVAL_DIR = tmpdir

            from app.services.evaluator import run_evaluation

            result = run_evaluation(top_k=5)

        assert result.metrics.total_questions == 2
        assert 0.0 <= result.metrics.precision_at_k <= 1.0
        assert 0.0 <= result.metrics.recall_at_k <= 1.0
        assert 0.0 <= result.metrics.mean_reciprocal_rank <= 1.0
        assert 0.0 <= result.metrics.avg_keyword_coverage <= 1.0
        assert result.metrics.avg_latency_ms >= 0
        assert len(result.per_question_results) == 2
        assert len(result.recommendations) >= 1
        assert result.eval_timestamp != ""
