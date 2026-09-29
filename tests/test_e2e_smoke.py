"""
tests/test_e2e_smoke.py — End-to-End STP Verification Smoke Test (< 300s)
"""
import time
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database

client = TestClient(app)


def test_stp_onboarding_velocity_smoke():
    """Verify end-to-end straight-through customer onboarding completes in under 300 seconds (REQ-N-001)."""
    init_database()
    start_time = time.time()

    # 1. Initialize session
    res1 = client.post("/api/v1/applications/session", json={
        "applicant_email": "fast.onboarding@enterprise.com",
        "applicant_phone": "+15550001111",
        "consent_given": True,
        "terms_accepted": True
    })
    assert res1.status_code == 201
    sess_id = res1.json()["session_id"]
    app_id = res1.json()["application_id"]

    # 2. OCR Scan
    res2 = client.post("/api/v1/kyc/ocr-scan", json={
        "session_id": sess_id,
        "document_type": "PASSPORT",
        "document_number": "P889900112"
    })
    assert res2.status_code == 200

    # 3. Verify Info
    res3 = client.post("/api/v1/kyc/verify-personal-info", json={
        "session_id": sess_id,
        "first_name": "Alexander",
        "last_name": "Hamilton",
        "document_number": "P889900112",
        "residential_address": "55 Wall Street",
        "city": "New York",
        "postal_code": "10005",
        "otp_code": "894210"
    })
    assert res3.status_code == 200

    # 4. Biometrics
    res4 = client.post("/api/v1/kyc/biometrics", json={
        "session_id": sess_id,
        "selfie_base64": "live_selfie_feed"
    })
    assert res4.status_code == 200

    # 5. AML Screening
    res5 = client.post("/api/v1/compliance/aml-screen", json={
        "session_id": sess_id,
        "full_name": "Alexander Hamilton",
        "date_of_birth": "1988-01-11",
        "nationality": "USA"
    })
    assert res5.status_code == 200

    # 6. CBS Account Provisioning
    res6 = client.post("/api/v1/accounts/create", json={
        "session_id": sess_id,
        "account_product_code": "SAVINGS_HIGH_YIELD",
        "initial_deposit": 250.00
    })
    assert res6.status_code == 201
    acc_num = res6.json()["account_number"]

    # 7. CMS Virtual Card Issuance
    res7 = client.post("/api/v1/cards/issue", json={
        "session_id": sess_id,
        "account_number": acc_num,
        "card_holder_name": "ALEXANDER HAMILTON"
    })
    assert res7.status_code == 201
    card_id = res7.json()["card_id"]

    # 8. Digital Wallet Push Tokenization
    res8 = client.post("/api/v1/cards/push-tokenize", json={
        "card_id": card_id,
        "wallet_provider": "APPLE_PAY"
    })
    assert res8.status_code == 200

    # 9. Query Final Application Dossier
    res9 = client.get(f"/api/v1/applications/{app_id}")
    assert res9.status_code == 200
    assert res9.json()["status"] == "COMPLETED"

    duration = time.time() - start_time
    assert duration < 300.0, f"STP Onboarding took {duration:.2f}s, exceeding 300s SLA"
