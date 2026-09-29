-- =============================================================================
-- Digital Savings Account Opening Platform - Database Seeds
-- =============================================================================

-- Seed an existing demo completed onboarding session
INSERT OR IGNORE INTO onboarding_sessions (
    session_id, application_id, applicant_email, applicant_phone, consent_given, terms_accepted, channel, status, current_step, created_at, expires_at
) VALUES (
    'sess_demo_001', 'app_demo_001', 'jane.doe@enterprise-bank.com', '+1-555-0199', 1, 1, 'web', 'COMPLETED', 'CARD_ISSUED', CURRENT_TIMESTAMP, datetime('now', '+1 day')
);

INSERT OR IGNORE INTO pii_vault (
    vault_id, application_id, encrypted_payload, key_version, created_at
) VALUES (
    'vlt_demo_001', 'app_demo_001', 'enc:aes256:7a8b9c0d1e2f3a4b5c6d7e8f:f8e7d6c5b4a3', 'v1-kms', CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO kyc_verifications (
    verification_id, session_id, document_type, document_number, first_name, last_name, date_of_birth, gender, nationality, expiry_date, mrz_valid, ocr_confidence, personal_info_verified, otp_verified, liveness_passed, liveness_confidence, face_match_confidence, anti_spoofing_status, aml_status, pep_match, sanction_match, risk_score, created_at
) VALUES (
    'kyc_demo_001', 'sess_demo_001', 'PASSPORT', 'P987654321', 'Jane', 'Doe', '1990-05-15', 'F', 'USA', '2030-05-15', 1, 0.99, 1, 1, 1, 0.99, 0.98, 'PASSED', 'CLEARED', 0, 0, 0, CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO accounts (
    account_id, application_id, cif_number, account_number, account_type, currency, balance, status, cbs_status, created_at
) VALUES (
    'acc_demo_001', 'app_demo_001', 'CIF-9901823', 'ACCT-8871029384', 'SAVINGS', 'USD', 500.00, 'ACTIVE', 'ACTIVE', CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO virtual_cards (
    card_id, account_number, card_holder_name, masked_pan, full_pan, expiry_date, cvv, network, status, wallet_provider, token_reference_id, token_cryptogram, tokenization_status, created_at
) VALUES (
    'crd_demo_001', 'ACCT-8871029384', 'JANE DOE', '4111 •••• •••• 9012', '4111222233339012', '09/29', '789', 'VISA', 'ACTIVE', 'APPLE_PAY', 'TOK-AP-881923', 'cryptogram_demo_hash_99182', 'TOKENIZED_SUCCESS', CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO saga_executions (
    saga_id, session_id, current_state, status, payload_json, step_history_json, created_at, updated_at
) VALUES (
    'saga_demo_001', 'sess_demo_001', 'CARD_ISSUANCE', 'COMPLETED', '{"applicant": "Jane Doe"}', '["CONSENT","OCR_SCAN","PERSONAL_INFO","BIOMETRIC_LIVENESS","AML_SCREENING","CBS_ACCOUNT_CREATION","CARD_ISSUANCE"]', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO audit_ledger (
    entry_id, timestamp, action, entity_id, actor, prev_hash, entry_hash, payload_json
) VALUES (
    'aud_genesis_000', CURRENT_TIMESTAMP, 'SYSTEM_INIT', 'SYS_CORE', 'system', '0000000000000000000000000000000000000000000000000000000000000000', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '{"event": "genesis_ledger"}'
);
