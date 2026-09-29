"""
Test Faceted Search Service & Query Builder (ARCH-1522, ARCH-1540, ARCH-1541, ARCH-1542)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database


@pytest.fixture(autouse=True)
def setup_db():
    init_database(reset=True)


client = TestClient(app)


def test_fulltext_search_query():
    """Verify search returns matching hits and response time in ms."""
    res = client.get("/api/v1/search?q=PostgreSQL")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert data["took_ms"] >= 0
    assert any("PostgreSQL" in h["title"] or "PostgreSQL" in h["snippet"] for h in data["hits"])


def test_search_faceting():
    """Verify faceted category and priority aggregations are calculated."""
    res = client.get("/api/v1/search")
    assert res.status_code == 200
    data = res.json()
    assert "facets" in data
    assert "by_status" in data["facets"]
    assert "by_priority" in data["facets"]
    assert "by_category" in data["facets"]
