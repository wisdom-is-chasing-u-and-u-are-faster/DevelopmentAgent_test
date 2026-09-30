import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_faceted_ticket_search():
    res = client.get("/api/v1/tickets?department=Database")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert all(t["department"] == "Database" for t in data["items"])

    res_kw = client.get("/api/v1/tickets?q=Failover")
    assert res_kw.status_code == 200
    assert res_kw.json()["total"] >= 1


def test_enterprise_metrics_endpoint():
    res = client.get("/api/v1/metrics")
    assert res.status_code == 200
    metrics = res.json()
    assert "mtta_minutes" in metrics
    assert "mttr_minutes" in metrics
    assert "sla_adherence_percent" in metrics
    assert "severity_distribution" in metrics
    assert metrics["mtta_minutes"] <= 5.0
