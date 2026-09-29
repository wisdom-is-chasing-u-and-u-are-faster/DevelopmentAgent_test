-- =============================================================================
-- Digital Savings Account Opening Platform - Relational Database Schema
-- =============================================================================

CREATE TABLE IF NOT EXISTS onboarding_sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    application_id VARCHAR(64) UNIQUE NOT NULL,
    applicant_email VARCHAR(255) NOT NULL,
    applicant_phone VARCHAR(50) NOT NULL,
    consent_given INTEGER NOT NULL DEFAULT 1,
    terms_accepted INTEGER NOT NULL DEFAULT 1,
    channel VARCHAR(50) NOT NULL DEFAULT 'web',
    status VARCHAR(50) NOT NULL DEFAULT 'SESSION_INITIALIZED',
    current_step VARCHAR(50) NOT NULL DEFAULT 'CONSENT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pii_vault (
    vault_id VARCHAR(64) PRIMARY KEY,
    application_id VARCHAR(64) NOT NULL,
    encrypted_payload TEXT NOT NULL,
    key_version VARCHAR(50) NOT NULL DEFAULT 'v1-kms',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES onboarding_sessions (application_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS kyc_verifications (
    verification_id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    document_number VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth VARCHAR(50) NOT NULL,
    gender VARCHAR(20),
    nationality VARCHAR(50) NOT NULL,
    expiry_date VARCHAR(50),
    mrz_valid INTEGER NOT NULL DEFAULT 1,
    ocr_confidence REAL NOT NULL DEFAULT 0.98,
    personal_info_verified INTEGER NOT NULL DEFAULT 1,
    otp_verified INTEGER NOT NULL DEFAULT 1,
    liveness_passed INTEGER NOT NULL DEFAULT 1,
    liveness_confidence REAL NOT NULL DEFAULT 0.99,
    face_match_confidence REAL NOT NULL DEFAULT 0.97,
    anti_spoofing_status VARCHAR(50) NOT NULL DEFAULT 'PASSED',
    aml_status VARCHAR(50) NOT NULL DEFAULT 'CLEARED',
    pep_match INTEGER NOT NULL DEFAULT 0,
    sanction_match INTEGER NOT NULL DEFAULT 0,
    risk_score INTEGER NOT NULL DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES onboarding_sessions (session_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id VARCHAR(64) PRIMARY KEY,
    application_id VARCHAR(64) NOT NULL,
    cif_number VARCHAR(64) UNIQUE NOT NULL,
    account_number VARCHAR(64) UNIQUE NOT NULL,
    account_type VARCHAR(50) NOT NULL DEFAULT 'SAVINGS',
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    balance REAL NOT NULL DEFAULT 100.00,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    cbs_status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES onboarding_sessions (application_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS virtual_cards (
    card_id VARCHAR(64) PRIMARY KEY,
    account_number VARCHAR(64) NOT NULL,
    card_holder_name VARCHAR(255) NOT NULL,
    masked_pan VARCHAR(50) NOT NULL,
    full_pan VARCHAR(50) NOT NULL,
    expiry_date VARCHAR(20) NOT NULL,
    cvv VARCHAR(10) NOT NULL,
    network VARCHAR(50) NOT NULL DEFAULT 'VISA',
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    wallet_provider VARCHAR(50),
    token_reference_id VARCHAR(100),
    token_cryptogram VARCHAR(255),
    tokenization_status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_number) REFERENCES accounts (account_number) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS saga_executions (
    saga_id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    current_state VARCHAR(50) NOT NULL DEFAULT 'CONSENT',
    status VARCHAR(50) NOT NULL DEFAULT 'IN_PROGRESS',
    payload_json TEXT NOT NULL DEFAULT '{}',
    step_history_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES onboarding_sessions (session_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_ledger (
    entry_id VARCHAR(64) PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    actor VARCHAR(100) NOT NULL DEFAULT 'system',
    prev_hash VARCHAR(128) NOT NULL,
    entry_hash VARCHAR(128) NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}'
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sessions_application ON onboarding_sessions (application_id);
CREATE INDEX IF NOT EXISTS idx_kyc_session ON kyc_verifications (session_id);
CREATE INDEX IF NOT EXISTS idx_accounts_cif ON accounts (cif_number);
CREATE INDEX IF NOT EXISTS idx_virtual_cards_acc ON virtual_cards (account_number);
CREATE INDEX IF NOT EXISTS idx_saga_session ON saga_executions (session_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_ledger (timestamp);
