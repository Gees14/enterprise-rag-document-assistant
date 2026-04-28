from typing import List, Optional

from app.core.config import settings
from app.core.errors import EmbeddingError
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """
    Generates dense vector embeddings using sentence-transformers.

    Default model: all-MiniLM-L6-v2
        → 384-dimensional cosine-similarity vectors
        → Fast inference (~10ms per batch on CPU)
        → No API key required

    Set EMBEDDING_MODEL in .env to switch models, e.g.:
        all-mpnet-base-v2       (768d, higher quality, slower)
        paraphrase-MiniLM-L6-v2 (384d, optimised for paraphrase tasks)
    """

    def __init__(self) -> None:
        self._model: Optional[object] = None
        self._model_name: str = settings.EMBEDDING_MODEL

    def _load_model(self) -> object:
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer  # lazy import

                logger.info("Loading embedding model.", model=self._model_name)
                self._model = SentenceTransformer(self._model_name)
                logger.info("Embedding model loaded successfully.", model=self._model_name)
            except ImportError as e:
                raise EmbeddingError(
                    "sentence-transformers is not installed. "
                    "Run: pip install sentence-transformers"
                ) from e
            except Exception as e:
                raise EmbeddingError(
                    f"Could not load embedding model '{self._model_name}': {e}"
                ) from e
        return self._model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of texts. Returns a list of float vectors."""
        if not texts:
            return []
        model = self._load_model()
        try:
            embeddings = model.encode(  # type: ignore[attr-defined]
                texts,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
            return embeddings.tolist()
        except Exception as e:
            raise EmbeddingError(f"Inference failed: {e}") from e

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query string. Uses the same model as document embedding."""
        vectors = self.embed_texts([query])
        return vectors[0]


# Module-level singleton — shared across all requests
embedding_service = EmbeddingService()
