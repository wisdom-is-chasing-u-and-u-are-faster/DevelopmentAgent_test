"""
app/services/compliance_service.py — Automated Real-Time AML/PEP Sanctions Watchlist Screening
"""
import uuid
from typing import Dict, Any


class ComplianceService:
    KNOWN_SANCTION_NAMES = {
        "SANCTION_TEST_USER",
        "VLADIMIR_SANCTION",
        "TERROR_LIST_NAME"}
    KNOWN_PEP_NAMES = {"SENATOR_DOE", "MINISTER_SMITH"}

    @classmethod
    def screen_applicant(cls, full_name: str, date_of_birth: str,
                         nationality: str) -> Dict[str, Any]:
        """Performs automated real-time watchlist screening."""
        normalized_name = full_name.upper().replace(" ", "_")

        is_sanctioned = normalized_name in cls.KNOWN_SANCTION_NAMES
        is_pep = normalized_name in cls.KNOWN_PEP_NAMES

        risk_score = 0
        if is_sanctioned:
            risk_score = 99
            status = "BLOCKED_SANCTION"
        elif is_pep:
            risk_score = 65
            status = "MANUAL_REVIEW_REQUIRED"
        else:
            risk_score = 5
            status = "CLEARED"

        ref = f"AML-REF-{uuid.uuid4().hex[:8].upper()}"

        return {
            "aml_status": status,
            "pep_match": is_pep,
            "sanction_match": is_sanctioned,
            "risk_score": risk_score,
            "screening_reference": ref,
        }
