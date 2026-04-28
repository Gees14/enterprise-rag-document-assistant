import os
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings
from app.core.errors import VectorStoreError
from app.core.logging import get_logger

logger = get_logger(__name__)


class VectorStoreService:
    """
    ChromaDB-backed vector store for document chunks.

    Uses cosine similarity (configured via hnsw:space metadata).
    Data persists across restarts in VECTOR_STORE_DIR.
    """

    def __init__(self) -> None:
        self._client: Optional[chromadb.PersistentClient] = None
        self._collection: Optional[chromadb.Collection] = None

    def _init(self) -> chromadb.Collection:
        if self._collection is None:
            persist_dir = os.path.abspath(settings.VECTOR_STORE_DIR)
            os.makedirs(persist_dir, exist_ok=True)
            try:
                self._client = chromadb.PersistentClient(
                    path=persist_dir,
                    settings=ChromaSettings(anonymized_telemetry=False),
                )
                self._collection = self._client.get_or_create_collection(
                    name=settings.CHROMA_COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"},
                )
                logger.info(
                    "ChromaDB initialized.",
                    path=persist_dir,
                    collection=settings.CHROMA_COLLECTION_NAME,
                )
            except Exception as e:
                raise VectorStoreError(f"Could not initialize ChromaDB: {e}") from e
        return self._collection

    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ) -> None:
        """Upsert chunks (text + embeddings + metadata) into ChromaDB."""
        collection = self._init()
        try:
            collection.upsert(
                ids=[c["chunk_id"] for c in chunks],
                documents=[c["text"] for c in chunks],
                embeddings=embeddings,
                metadatas=[
                    {
                        "document_id": c["document_id"],
                        "filename": c["filename"],
                        "page_number": c["page_number"],
                        "character_start": c["character_start"],
                        "character_end": c["character_end"],
                    }
                    for c in chunks
                ],
            )
            logger.info("Chunks upserted.", count=len(chunks))
        except Exception as e:
            raise VectorStoreError(f"Failed to add chunks: {e}") from e

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the top-k most similar chunks for a query embedding.

        Returns a list of dicts with keys:
            chunk_id, text, metadata, score (cosine similarity, 0-1)
        """
        collection = self._init()
        total = collection.count()
        if total == 0:
            return []

        effective_k = min(top_k, total)
        where_filter = (
            {"document_id": {"$in": document_ids}} if document_ids else None
        )

        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=effective_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            raise VectorStoreError(f"Query failed: {e}") from e

        chunks: List[Dict[str, Any]] = []
        ids = results.get("ids", [[]])[0]
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]

        for chunk_id, text, meta, dist in zip(ids, docs, metas, dists):
            # ChromaDB cosine distance is in [0, 2]; convert to similarity [0, 1]
            similarity = max(0.0, 1.0 - dist / 2.0)
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "text": text,
                    "metadata": meta,
                    "score": round(similarity, 4),
                }
            )

        return chunks

    def delete_by_document_id(self, document_id: str) -> int:
        """Delete all chunks belonging to a document. Returns deleted count."""
        collection = self._init()
        try:
            existing = collection.get(where={"document_id": document_id})
            ids_to_delete = existing.get("ids", [])
            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
            logger.info("Deleted chunks.", document_id=document_id, count=len(ids_to_delete))
            return len(ids_to_delete)
        except Exception as e:
            raise VectorStoreError(f"Failed to delete chunks: {e}") from e

    def count(self) -> int:
        """Return total number of chunks in the collection."""
        collection = self._init()
        return collection.count()

    def is_healthy(self) -> bool:
        """Return True if ChromaDB is reachable."""
        try:
            self._init()
            return True
        except Exception:
            return False


vector_store_service = VectorStoreService()
