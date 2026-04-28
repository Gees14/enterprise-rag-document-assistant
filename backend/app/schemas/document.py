from typing import List, Optional

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: str
    filename: str
    upload_time: str
    status: str
    page_count: int
    chunk_count: int
    file_size_bytes: int


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


class IndexResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    chunk_count: int
    page_count: int
    message: str


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    file_size_bytes: int
    message: str


class DeleteResponse(BaseModel):
    document_id: str
    message: str
