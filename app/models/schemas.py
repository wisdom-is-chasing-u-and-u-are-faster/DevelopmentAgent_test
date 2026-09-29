"""
app/models/schemas.py — Pydantic Data Contracts & RFC-7807 Models
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# RFC-7807 Structured Problem Details
# -----------------------------------------------------------------------------
class ProblemDetail(BaseModel):
    type: str = Field(
        default="about:blank",
        description="URI reference identifying the problem type")
    title: str = Field(...,
                       description="Short, human-readable summary of the problem")
    status: int = Field(..., description="HTTP status code")
    detail: str = Field(...,
                        description="Human-readable explanation specific to this occurrence")
    instance: Optional[str] = Field(
        default=None,
        description="URI reference identifying the specific occurrence")
    invalid_params: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Details about invalid parameters")


# -----------------------------------------------------------------------------
# Health & Status
# -----------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str = "HEALTHY"
    service: str = "digital-savings-account-opening"
    version: str = "1.0.0"


# -----------------------------------------------------------------------------
# Step 1: Session Initialization & Consent
# -----------------------------------------------------------------------------
class SessionInitRequest(BaseModel):
    applicant_email: str
    applicant_phone: str
    consent_given: bool = True
    terms_accepted: bool = True
    channel: str = "web"


class SessionInitResponse(BaseModel):
    session_id: str
    application_id: str
    status: str
    created_at: str
    expires_at: str


# -----------------------------------------------------------------------------
# Step 2: Document OCR Scanning & MRZ Checksum
# -----------------------------------------------------------------------------
class OCRScanRequest(BaseModel):
    session_id: str
    document_type: str = "PASSPORT"  # PASSPORT | NATIONAL_ID | DRIVER_LICENSE
    document_front_base64: Optional[str] = None
    document_back_base64: Optional[str] = None
    document_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None


class OCRScanResponse(BaseModel):
    session_id: str
    document_type: str
    document_number: str
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    nationality: str
    expiry_date: str
    mrz_valid: bool
    ocr_confidence: float


# -----------------------------------------------------------------------------
# Step 3: Verify Personal Information & OTP
# -----------------------------------------------------------------------------
class VerifyPersonalInfoRequest(BaseModel):
    session_id: str
    first_name: str
    last_name: str
    document_number: str
    residential_address: str
    city: str
    postal_code: str
    otp_code: Optional[str] = "123456"


class VerifyPersonalInfoResponse(BaseModel):
    session_id: str
    personal_info_verified: bool
    otp_verified: bool
    next_step: str = "BIOMETRIC_LIVENESS"


# -----------------------------------------------------------------------------
# Step 4: 3D Passive Biometric Liveness Check
# -----------------------------------------------------------------------------
class BiometricsRequest(BaseModel):
    session_id: str
    selfie_base64: Optional[str] = None
    liveness_frames: Optional[List[str]] = None


class BiometricsResponse(BaseModel):
    session_id: str
    liveness_passed: bool
    liveness_confidence: float
    face_match_confidence: float
    anti_spoofing_status: str


# -----------------------------------------------------------------------------
# Step 5: Real-Time AML / PEP Watchlist Screening
# -----------------------------------------------------------------------------
class AMLScreenRequest(BaseModel):
    session_id: str
    full_name: str
    date_of_birth: str
    nationality: str


class AMLScreenResponse(BaseModel):
    session_id: str
    aml_status: str
    pep_match: bool
    sanction_match: bool
    risk_score: int
    screening_reference: str


# -----------------------------------------------------------------------------
# Step 6: Core Banking System (CBS) Account Creation
# -----------------------------------------------------------------------------
class AccountCreateRequest(BaseModel):
    session_id: str
    account_product_code: str = "SAVINGS_STANDARD"
    initial_deposit: float = 100.00
    currency: str = "USD"


class AccountCreateResponse(BaseModel):
    application_id: str
    cif_number: str
    account_number: str
    account_type: str
    currency: str
    balance: float
    cbs_status: str


# -----------------------------------------------------------------------------
# Step 7: Virtual Debit Card & Push Tokenization
# -----------------------------------------------------------------------------
class CardIssueRequest(BaseModel):
    session_id: str
    account_number: str
    card_holder_name: str
    card_network: str = "VISA"


class CardIssueResponse(BaseModel):
    card_id: str
    account_number: str
    masked_pan: str
    full_pan: str
    expiry_date: str
    cvv: str
    card_holder_name: str
    status: str
    network: str


class CardPushTokenizeRequest(BaseModel):
    card_id: str
    wallet_provider: str = "APPLE_PAY"  # APPLE_PAY | GOOGLE_PAY
    device_id: Optional[str] = "dev_iphone_15_pro"


class CardPushTokenizeResponse(BaseModel):
    card_id: str
    wallet_provider: str
    token_reference_id: str
    tokenization_status: str
    token_cryptogram: str


# -----------------------------------------------------------------------------
# Application Dossier & Saga Progression
# -----------------------------------------------------------------------------
class ApplicationDetailsResponse(BaseModel):
    application_id: str
    session_id: str
    applicant_name: str
    cif_number: str
    account_number: str
    card_id: str
    masked_pan: str
    status: str
    stp_processed: bool
    elapsed_seconds: float


class SagaStepStatus(BaseModel):
    name: str
    status: str


class OnboardingStatusResponse(BaseModel):
    session_id: str
    current_step: str
    step_progress_pct: int
    saga_state: str
    steps: List[SagaStepStatus]


# -----------------------------------------------------------------------------
# Cryptographic Audit Ledger
# -----------------------------------------------------------------------------
class AuditLedgerEntry(BaseModel):
    entry_id: str
    timestamp: str
    action: str
    entity_id: str
    actor: str
    prev_hash: str
    entry_hash: str
    payload_json: Optional[str] = "{}"


class AuditLedgerResponse(BaseModel):
    total_entries: int
    ledger: List[AuditLedgerEntry]
