"""Tests for Phase 6 — API contract tests."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client. Imports here to avoid loading corpus at import time."""
    from milestone1.phase6_api.app import app
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "groq_configured" in data
        assert "corpus_size" in data


class TestMetaEndpoint:
    def test_meta_returns_lists(self, client):
        response = client.get("/api/v1/meta")
        assert response.status_code == 200
        data = response.json()
        assert "locations" in data
        assert "cuisines" in data
        assert isinstance(data["locations"], list)
        assert isinstance(data["cuisines"], list)
        assert data["total_restaurants"] > 0


class TestRecommendationsEndpoint:
    def test_missing_location_422(self, client):
        response = client.post("/api/v1/recommendations", json={})
        assert response.status_code == 422

    def test_invalid_location_422(self, client):
        response = client.post(
            "/api/v1/recommendations",
            json={"location": "NonExistentPlace12345"},
        )
        assert response.status_code == 422
