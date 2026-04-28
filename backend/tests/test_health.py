import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "app_name" in data


def test_health_ready():
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "vector_store" in data
    assert "chunk_count" in data
    assert "llm_enabled" in data
    assert isinstance(data["chunk_count"], int)
    assert isinstance(data["llm_enabled"], bool)


def test_health_has_version():
    response = client.get("/health")
    data = response.json()
    assert data["version"] == "1.0.0"
