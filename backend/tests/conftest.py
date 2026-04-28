import os
import sys
import tempfile

import pytest

# Ensure backend/app is importable from tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Use a temp directory for all data during tests
os.environ.setdefault("UPLOAD_DIR", tempfile.mkdtemp(prefix="rag_test_uploads_"))
os.environ.setdefault("VECTOR_STORE_DIR", tempfile.mkdtemp(prefix="rag_test_vectors_"))
os.environ.setdefault("EVAL_DIR", tempfile.mkdtemp(prefix="rag_test_eval_"))
os.environ.setdefault("DOCUMENTS_DB", os.path.join(tempfile.mkdtemp(), "documents.json"))
os.environ.setdefault("OPENAI_API_KEY", "")


@pytest.fixture
def sample_pages():
    """A minimal list of page dicts mimicking document_loader output."""
    return [
        {
            "page_number": 1,
            "text": (
                "Introduction to machine learning. "
                "Machine learning is a subfield of artificial intelligence. "
                "It enables computers to learn from data without being explicitly programmed."
            ),
        },
        {
            "page_number": 2,
            "text": (
                "Supervised learning uses labeled training data. "
                "The model learns to map inputs to outputs. "
                "Common algorithms include linear regression and decision trees."
            ),
        },
        {
            "page_number": 3,
            "text": (
                "Evaluation metrics are critical for assessing model performance. "
                "Precision, recall, and F1 score are commonly used in classification tasks."
            ),
        },
    ]


@pytest.fixture
def sample_document_id():
    return "test-doc-00000000-0000-0000-0000-000000000001"


@pytest.fixture
def sample_filename():
    return "machine_learning_intro.pdf"
