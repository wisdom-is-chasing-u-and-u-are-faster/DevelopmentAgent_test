"""
tests/test_api.py — REST API Endpoint & RFC-7807 Verification Tests
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_health_probe():
    """Verify health endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"


def test_create_session_success():
    """Verify session creation endpoint."""
    payload = {
        "applicant_email": "unit.test@enterprise.com",
        "applicant_phone": "+15551234567",
        "consent_given": True,
        "terms_accepted": True,
        "channel": "web"
    }
    response = client.post(
        "/api/v1/applications/session",
        json=payload,
        headers={
            "Idempotency-Key": "test-key-1"})
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert data["status"] == "SESSION_INITIALIZED"


def test_rfc7807_error_handling_invalid_payload():
    """Verify RFC-7807 problem details returned on invalid request payload (REQ-F-015)."""
    payload = {
        "applicant_email": "invalid-email-format",
        "applicant_phone": "+15551234567"
    }
    response = client.post("/api/v1/applications/session", json=payload)
    assert response.status_code == 400
    assert response.headers.get("content-type") == "application/problem+json"
    data = response.json()
    assert data["status"] == 400
    assert "title" in data
    assert "detail" in data


def test_jwt_auth_rejection():
    """Verify HTTP 401 Unauthorized returned on invalid JWT authorization header (REQ-F-016)."""
    response = client.post(
        "/api/v1/applications/session",
        json={"applicant_email": "test@bank.com",
              "applicant_phone": "+15551234567"},
        headers={"Authorization": "Bearer invalid_token_xyz"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["status"] == 401


def test_full_onboarding_lifecycle_api():
    """Test full onboarding API lifecycle through all endpoints."""
    # 1. Session
    res_sess = client.post(
        "/api/v1/applications/session",
        json={
            "applicant_email": "e2e.user@bank.com",
            "applicant_phone": "+15559876543"}
    )
    assert res_sess.status_code == 201
    sess_id = res_sess.json()["session_id"]
    app_id = res_sess.json()["application_id"]
    assert app_id.startswith("app_")

    # 2. OCR Scan
    res_ocr = client.post(
        "/api/v1/kyc/ocr-scan",
        json={
            "session_id": sess_id,
            "document_type": "PASSPORT",
            "document_number": "P123456789"}
    )
    assert res_ocr.status_code == 200
    assert res_ocr.json()["mrz_valid"] is True

    # 3. Personal Info
    res_info = client.post(
        "/api/v1/kyc/verify-personal-info",
        json={
            "session_id": sess_id,
            "first_name": "Alexander",
            "last_name": "Hamilton",
            "document_number": "P123456789",
            "residential_address": "55 Wall St",
            "city": "New York",
            "postal_code": "10005",
            "otp_code": "123456"
        }
    )
    assert res_info.status_code == 200

    # 4. Biometrics
    res_bio = client.post(
        "/api/v1/kyc/biometrics",
        json={"session_id": sess_id, "selfie_base64": "selfie_data"}
    )
    assert res_bio.status_code == 200
    assert res_bio.json()["liveness_passed"] is True

    # 5. AML Screen
    res_aml = client.post(
        "/api/v1/compliance/aml-screen",
        json={
            "session_id": sess_id,
            "full_name": "Alexander Hamilton",
            "date_of_birth": "1988-01-11",
            "nationality": "USA"}
    )
    assert res_aml.status_code == 200
    assert res_aml.json()["aml_status"] == "CLEARED"

    # 6. Account Creation
    res_acc = client.post(
        "/api/v1/accounts/create",
        json={
            "session_id": sess_id,
            "account_product_code": "SAVINGS_HIGH_YIELD",
            "initial_deposit": 100.0}
    )
    assert res_acc.status_code == 201
    acc_num = res_acc.json()["account_number"]

    # 7. Card Issue
    res_card = client.post(
        "/api/v1/cards/issue",
        json={
            "session_id": sess_id,
            "account_number": acc_num,
            "card_holder_name": "ALEXANDER HAMILTON"}
    )
    assert res_card.status_code == 201
    card_id = res_card.json()["card_id"]

    # 8. Push Tokenize
    res_tok = client.post(
        "/api/v1/cards/push-tokenize",
        json={"card_id": card_id, "wallet_provider": "APPLE_PAY"}
    )
    assert res_tok.status_code == 200
    assert res_tok.json()["tokenization_status"] == "TOKENIZED_SUCCESS"

    # 9. Query Status
    res_stat = client.get(f"/api/v1/onboarding/status/{sess_id}")
    assert res_stat.status_code == 200
    assert res_stat.json()["saga_state"] == "COMPLETED"
