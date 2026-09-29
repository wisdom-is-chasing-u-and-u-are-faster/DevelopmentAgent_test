"""
tests/test_wiring.py — Frontend Static Mounting & Cross-Tier Integration Tests
"""
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_static_index_mount():
    """Verify visiting root '/' returns index.html."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Digital Savings Account Opening Platform" in response.text
    assert "stepper" in response.text


def test_static_pages_mount():
    """Verify subpages in /pages/ return 200 OK."""
    pages = [
        "/pages/welcome_and_consent.html",
        "/pages/scan_identity_document.html",
        "/pages/verify_personal_information.html",
        "/pages/biometric_liveness_check.html",
        "/pages/application_review_and_submit.html",
        "/pages/application_complete_and_virtual_card_issued.html",
    ]
    for page in pages:
        res = client.get(page)
        assert res.status_code == 200, f"Failed on {page}"
        assert "BankingAPI" in res.text or "Enterprise Digital Bank" in res.text


def test_static_js_api_client():
    """Verify /js/api.js is served properly."""
    response = client.get("/js/api.js")
    assert response.status_code == 200
    assert "BankingAPI" in response.text
