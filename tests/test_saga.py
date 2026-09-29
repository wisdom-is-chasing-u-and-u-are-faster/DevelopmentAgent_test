"""
tests/test_saga.py — Saga State Engine & Compensation Tests
"""
import pytest
from app.db.init_db import init_database
from app.services.saga_orchestrator import SagaOrchestrator
from app.services.ocr_service import OCRService
from app.services.biometrics_service import BiometricsService
from app.services.compliance_service import ComplianceService
from app.services.cbs_adapter import CBSAdapter
from app.services.cms_hsm_adapter import CMSHSMAdapter


def test_saga_orchestration_flow():
    """Verify full Saga state progression from consent to card issuance."""
    init_database()
    session_id = "sess_saga_test_001"

    # Step 1: Init
    saga_id = SagaOrchestrator.initialize_saga(
        session_id, {"email": "test@bank.com"})
    assert saga_id.startswith("saga_")

    # Step 2: OCR
    res_ocr = SagaOrchestrator.transition_state(
        session_id, "OCR_SCAN", {"doc": "PASSPORT"})
    assert res_ocr["current_step"] == "OCR_SCAN"

    # Step 3: Personal Info
    res_info = SagaOrchestrator.transition_state(
        session_id, "PERSONAL_INFO", {"name": "Alex"})
    assert res_info["current_step"] == "PERSONAL_INFO"

    # Step 4: Biometrics
    res_bio = SagaOrchestrator.transition_state(
        session_id, "BIOMETRIC_LIVENESS", {"liveness": True})
    assert res_bio["current_step"] == "BIOMETRIC_LIVENESS"

    # Step 5: AML
    res_aml = SagaOrchestrator.transition_state(
        session_id, "AML_SCREENING", {"status": "CLEARED"})
    assert res_aml["current_step"] == "AML_SCREENING"

    # Step 6: CBS
    res_cbs = SagaOrchestrator.transition_state(
        session_id, "CBS_ACCOUNT_CREATION", {
            "account": "ACCT-001"})
    assert res_cbs["current_step"] == "CBS_ACCOUNT_CREATION"

    # Step 7: Card Issue
    res_card = SagaOrchestrator.transition_state(
        session_id, "CARD_ISSUANCE", {"card": "CARD-001"})
    assert res_card["current_step"] == "CARD_ISSUANCE"
    assert res_card["saga_status"] == "COMPLETED"

    progress = SagaOrchestrator.get_progress(session_id)
    assert progress["step_progress_pct"] == 100
    assert progress["saga_state"] == "COMPLETED"


def test_saga_compensating_rollback():
    """Verify compensating rollback on downstream failure."""
    init_database()
    session_id = "sess_rollback_001"

    SagaOrchestrator.initialize_saga(
        session_id, {"email": "rollback@bank.com"})
    SagaOrchestrator.transition_state(session_id, "OCR_SCAN")

    # Trigger compensation
    res = SagaOrchestrator.compensate_and_rollback(
        session_id, "Biometric Face Match Failed")
    assert res["status"] == "ROLLED_BACK_QUARANTINED"
    assert res["compensation_executed"] is True
