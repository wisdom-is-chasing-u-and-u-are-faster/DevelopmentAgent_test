import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_system_health_readiness():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_full_lifecycle_e2e_journey():
    res_ingest = client.post("/api/v1/tickets", json={
        "title": "Global Edge CDN Routing Cache Outage",
        "description": "502 Bad Gateway responses across North American CDN edge nodes.",
        "priority": "P1",
        "department": "Infrastructure",
        "category": "outage",
        "requester_name": "NOC Operations",
        "requester_email": "noc@enterprise.internal"
    })
    assert res_ingest.status_code == 201
    ticket_id = res_ingest.json()["id"]

    res_disp = client.post(f"/api/v1/tickets/{ticket_id}/dispatch", json={})
    assert res_disp.status_code == 200
    assert res_disp.json()["assigned_agent_id"] is not None

    res_prog = client.patch(f"/api/v1/tickets/{ticket_id}/status", json={
        "status": "IN_PROGRESS",
        "expected_version": 1,
        "actor": "Alex Mercer"
    })
    assert res_prog.status_code == 200
    assert res_prog.json()["version"] == 2

    res_resolve = client.patch(f"/api/v1/tickets/{ticket_id}/status", json={
        "status": "RESOLVED",
        "expected_version": 2,
        "comment": "Edge routing rules flushed and validated.",
        "actor": "Alex Mercer"
    })
    assert res_resolve.status_code == 200
    assert res_resolve.json()["status"] == "RESOLVED"

    res_detail = client.get(f"/api/v1/tickets/{ticket_id}")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert len(detail["history"]) >= 3


def test_static_html_routes():
    routes = [
        "/",
        "/index.html",
        "/dashboard.html",
        "/ticket-queue.html",
        "/ticket-detail.html",
        "/advanced-search.html",
        "/new-ticket-form.html",
        "/user_settings.html",
        "/audit.html",
        "/pages/dashboard.html",
        "/pages/ticket-queue.html"
    ]
    for route in routes:
        res = client.get(route)
        assert res.status_code == 200, f"Route {route} returned status {res.status_code}"
