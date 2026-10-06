"""
QA Persona v2 -- auto-generated tests
Service: app
Suite:   unit
Source:  test_strategy/plans/app__unit.json
Generated: 2024-07-12T17:01:21.135219Z
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

from app.main import app
from app.models.schemas import (
    SessionInitRequest, OCRScanRequest, VerifyPersonalInfoRequest, AccountCreateRequest
)

# Set a consistent timestamp for reproducible tests
NOW = datetime.now(timezone.utc)
NOW_ISO = NOW.isoformat()
EXPIRES_ISO = (NOW + timedelta(days=1)).isoformat()

@pytest.fixture
def client():
    """Fixture to provide a test client for the FastAPI application."""
    with TestClient(app) as c:
        yield c

def test_health_check_returns_success(client: TestClient):
    """Verifies the health_check function returns a success status.

    test_id: app__unit__001
    target: health_check
    requirement_id: no requirement
    ac_ids: none
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["service"] == "digital-savings-account-opening"
    assert data["version"] == "1.0.0"

@patch("app.api.router.AuditService.record_event")
@patch("app.api.router.SagaOrchestrator.initialize_saga")
@patch("app.api.router.get_db_connection")
def test_create_session_with_mocked_dependencies(mock_get_db, mock_init_saga, mock_record_event, client: TestClient):
    """Verifies create_session function logic with mocked dependencies.

    test_id: app__unit__002
    target: create_session
    requirement_id: no requirement
    ac_ids: none
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    request_payload = SessionInitRequest(
        applicant_email="test@example.com",
        applicant_phone="1234567890"
    )

    response = client.post(
        "/api/v1/applications/session",
        json=request_payload.model_dump(),
        headers={"Idempotency-Key": "test-key-123"}
    )

    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert "application_id" in data
    assert data["status"] == "SESSION_INITIALIZED"

    mock_get_db.assert_called_once()
    assert mock_cursor.execute.call_count == 2
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()
    mock_init_saga.assert_called_once()
    mock_record_event.assert_called_once()

@patch("app.api.router.SagaOrchestrator.transition_state")
@patch("app.api.router.OCRService.parse_document")
@patch("app.api.router.get_db_connection")
def test_ocr_scan_document_with_mocked_service(mock_get_db, mock_parse_doc, mock_transition_state, client: TestClient):
    """Verifies ocr_scan_document function logic with a mocked OCR service.

    test_id: app__unit__003
    target: ocr_scan_document
    requirement_id: no requirement
    ac_ids: none
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_ocr_result = {
        "document_type": "PASSPORT",
        "document_number": "P123456",
        "first_name": "Test",
        "last_name": "User",
        "date_of_birth": "1990-01-01",
        "gender": "M",
        "nationality": "USA",
        "expiry_date": "2030-01-01",
        "mrz_valid": True,
        "ocr_confidence": 0.95,
    }
    mock_parse_doc.return_value = mock_ocr_result

    request_payload = OCRScanRequest(session_id="sess_123", document_type="PASSPORT")

    response = client.post(
        "/api/v1/kyc/ocr-scan",
        json=request_payload.model_dump()
    )

    assert response.status_code == 200
    mock_parse_doc.assert_called_once()
    mock_transition_state.assert_called_once_with("sess_123", "OCR_SCAN", mock_ocr_result)
    assert response.json()["document_number"] == "P123456"
    assert response.json()["ocr_confidence"] == 0.95

@patch("app.api.router.SagaOrchestrator.transition_state")
@patch("app.api.router.get_db_connection")
def test_verify_personal_information_logic(mock_get_db, mock_transition_state, client: TestClient):
    """Verifies verify_personal_information function logic with mocked DB.

    test_id: app__unit__004
    target: verify_personal_information
    requirement_id: no requirement
    ac_ids: none
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    request_payload = VerifyPersonalInfoRequest(
        session_id="sess_123",
        first_name="Test",
        last_name="User",
        document_number="D123",
        residential_address="123 Main St",
        city="Anytown",
        postal_code="12345"
    )

    response = client.post(
        "/api/v1/kyc/verify-personal-info",
        json=request_payload.model_dump()
    )

    assert response.status_code == 200
    data = response.json()
    assert data["personal_info_verified"] is True
    assert data["otp_verified"] is True

    mock_get_db.assert_called_once()
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()
    mock_transition_state.assert_called_once()

@patch("app.api.router.SagaOrchestrator.transition_state")
@patch("app.api.router.CBSAdapter.provision_account")
@patch("app.api.router.get_db_connection")
def test_create_cbs_account_handles_idempotency(mock_get_db, mock_provision_account, mock_transition_state, client: TestClient):
    """Verifies create_cbs_account function handles a successful creation.

    test_id: app__unit__005
    target: create_cbs_account
    requirement_id: no requirement
    ac_ids: none
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"application_id": "app_12345"}

    mock_cbs_response = {
        "application_id": "app_12345",
        "cif_number": "CIF-123",
        "account_number": "ACCT-456",
        "account_type": "SAVINGS",
        "currency": "USD",
        "balance": 100.0,
        "cbs_status": "ACTIVE"
    }
    mock_provision_account.return_value = mock_cbs_response

    request_payload = AccountCreateRequest(
        session_id="sess_abc",
        initial_deposit=100.0
    )

    response1 = client.post(
        "/api/v1/accounts/create",
        json=request_payload.model_dump(),
        headers={"Idempotency-Key": "unique-key-for-cbs"}
    )

    assert response1.status_code == 201
    assert response1.json()["account_number"] == "ACCT-456"
    mock_provision_account.assert_called_once_with(
        application_id="app_12345",
        account_product_code="SAVINGS_STANDARD",
        initial_deposit=100.0,
        currency="USD"
    )
    mock_transition_state.assert_called_once_with("sess_abc", "CBS_ACCOUNT_CREATION", mock_cbs_response)

@patch("app.api.router.get_db_connection")
def test_get_application_details_logic(mock_get_db, client: TestClient):
    """Verifies get_application_details function logic with mocked data source.

    test_id: app__unit__006
    target: get_application_details
    requirement_id: no requirement
    ac_ids: none
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_row = {
        "session_id": "sess_xyz",
        "application_id": "app_xyz",
        "status": "COMPLETED",
        "created_at": NOW_ISO,
        "first_name": "Jane",
        "last_name": "Doe",
        "cif_number": "CIF-789",
        "account_number": "ACCT-987",
        "card_id": "card-654",
        "masked_pan": "4111 •••• •••• 1234"
    }
    mock_cursor.fetchone.return_value = mock_row

    response = client.get("/api/v1/applications/app_xyz")

    assert response.status_code == 200
    data = response.json()
    assert data["application_id"] == "app_xyz"
    assert data["applicant_name"] == "Jane Doe"
    assert data["account_number"] == "ACCT-987"

    mock_get_db.assert_called_once()
    mock_cursor.execute.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("app.api.router.AuditService.get_ledger")
def test_get_audit_ledger_with_pagination(mock_get_ledger, client: TestClient):
    """Verifies get_audit_ledger function correctly applies the 'limit' parameter.

    test_id: app__unit__007
    target: get_audit_ledger
    requirement_id: no requirement
    ac_ids: none
    """
    mock_records = [
        {
            "entry_id": f"aud_{i}",
            "timestamp": NOW_ISO,
            "action": "TEST_ACTION",
            "entity_id": "ent_123",
            "actor": "system",
            "prev_hash": "hash_prev",
            "entry_hash": "hash_curr",
            "payload_json": "{}"
        } for i in range(10)
    ]
    mock_get_ledger.return_value = mock_records

    response = client.get("/api/v1/audit/ledger?limit=10")

    assert response.status_code == 200
    mock_get_ledger.assert_called_once_with(limit=10)
    data = response.json()
    assert data["total_entries"] == 10
    assert len(data["ledger"]) == 10
    assert data["ledger"][0]["entry_id"] == "aud_0"
