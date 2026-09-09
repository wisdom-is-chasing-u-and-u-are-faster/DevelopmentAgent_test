import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    test_db_file = str(tmp_path / "test_cosmetics.db")
    monkeypatch.setenv("COSMETICS_DB_PATH", test_db_file)
    init_database(test_db_file)
    yield


client = TestClient(app)


def test_shade_finder_match_warm_medium():
    """AC: A user can successfully complete the shade finder quiz and be presented with a recommended product shade."""
    payload = {
        "skin_tone": "Medium",
        "undertone": "Warm",
        "finish_preference": "Dewy",
        "coverage": "Medium"
    }
    response = client.post("/api/v1/shade-finder/match", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "matched_shade_id" in data
    assert "shade_name" in data
    assert data["confidence_score"] > 90.0
    assert data["recommended_product"]["name"] is not None


def test_shade_finder_match_cool_fair():
    """AC: A user can successfully complete the shade finder quiz and be presented with a recommended product shade."""
    payload = {
        "skin_tone": "Fair",
        "undertone": "Cool",
        "finish_preference": "Natural",
        "coverage": "Full"
    }
    response = client.post("/api/v1/shade-finder/match", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["matched_shade_id"] > 0
