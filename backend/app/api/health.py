from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings
from app.services.vector_store import vector_store_service

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str
    app_name: str


class ReadinessResponse(BaseModel):
    status: str
    vector_store: str
    chunk_count: int
    llm_enabled: bool


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        app_name=settings.APP_NAME,
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check() -> ReadinessResponse:
    vs_healthy = vector_store_service.is_healthy()
    chunk_count = vector_store_service.count() if vs_healthy else 0

    return ReadinessResponse(
        status="ready" if vs_healthy else "degraded",
        vector_store="ok" if vs_healthy else "unavailable",
        chunk_count=chunk_count,
        llm_enabled=settings.llm_enabled,
    )
