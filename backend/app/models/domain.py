import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────
# Domain models
# ─────────────────────────────────────────────


class DocumentStatus:
    UPLOADED = "uploaded"
    INDEXING = "indexing"
    INDEXED = "indexed"
    FAILED = "failed"


class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    file_path: str
    upload_time: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    status: str = DocumentStatus.UPLOADED
    page_count: int = 0
    chunk_count: int = 0
    file_size_bytes: int = 0


class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    page_number: int
    text: str
    character_start: int
    character_end: int


# ─────────────────────────────────────────────
# Document repository — JSON-backed persistence
# Single-user local use only; not safe for concurrent writes.
# ─────────────────────────────────────────────


class DocumentRepository:
    def __init__(self, db_path: str = settings.DOCUMENTS_DB):
        self._db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def _load(self) -> Dict[str, Document]:
        if not os.path.exists(self._db_path):
            return {}
        try:
            with open(self._db_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return {doc_id: Document(**data) for doc_id, data in raw.items()}
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Could not parse documents.json; starting fresh.", error=str(e))
            return {}

    def _save(self, docs: Dict[str, Document]) -> None:
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        with open(self._db_path, "w", encoding="utf-8") as f:
            json.dump(
                {doc_id: doc.model_dump() for doc_id, doc in docs.items()},
                f,
                indent=2,
            )

    def save(self, document: Document) -> Document:
        docs = self._load()
        docs[document.id] = document
        self._save(docs)
        return document

    def get(self, document_id: str) -> Optional[Document]:
        docs = self._load()
        return docs.get(document_id)

    def list_all(self) -> List[Document]:
        return list(self._load().values())

    def delete(self, document_id: str) -> bool:
        docs = self._load()
        if document_id not in docs:
            return False
        del docs[document_id]
        self._save(docs)
        return True

    def update_status(
        self,
        document_id: str,
        status: str,
        chunk_count: int = 0,
        page_count: int = 0,
    ) -> Optional[Document]:
        docs = self._load()
        if document_id not in docs:
            return None
        doc = docs[document_id]
        doc.status = status
        if chunk_count:
            doc.chunk_count = chunk_count
        if page_count:
            doc.page_count = page_count
        self._save(docs)
        return doc


document_repository = DocumentRepository()
