from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Enterprise RAG Document Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Storage paths (relative to backend working directory)
    UPLOAD_DIR: str = "data/uploads"
    VECTOR_STORE_DIR: str = "data/vector_store"
    EVAL_DIR: str = "data/eval"
    DOCUMENTS_DB: str = "data/documents.json"

    # Embeddings
    # Default: all-MiniLM-L6-v2 → 384-dimensional cosine-similarity vectors
    # Alternatives: all-mpnet-base-v2 (768d), paraphrase-multilingual-MiniLM-L12-v2
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Chunking
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64

    # Retrieval
    DEFAULT_TOP_K: int = 5
    MIN_SIMILARITY_SCORE: float = 0.0

    # LLM Generation (all optional — system falls back to retrieval-only)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_MAX_TOKENS: int = 1024
    LLM_TEMPERATURE: float = 0.2

    # ChromaDB
    CHROMA_COLLECTION_NAME: str = "rag_documents"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # File upload limits
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [".pdf"]

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def llm_enabled(self) -> bool:
        return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY.strip())


settings = Settings()
