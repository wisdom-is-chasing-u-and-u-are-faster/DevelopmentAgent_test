"""
Tests for Story ARCH-S3: Offset-at-Checkout and Transactional Carbon Ledger
Covers Gherkin Scenarios 13 to 18.
"""
from app.services.offset_service import OffsetService
from app.services.ledger_service import LedgerService


def test_scenario_13_successful_purchase_offset_via_patch(client):
    """
    Scenario 13: Successful purchase of carbon offsets via Patch API (Positive)
    Given a customer completes an order with "Offset-at-Checkout" enabled (5.1 kg CO2e)
    When Order Service processes offset purchase
    Then Patch API returns transaction ID and certificate URL
    """
    payload = {
        "order_id": "ord_884729103984",
        "customer_id": "cust_usr_392019",
        "total_carbon_kg": 5.1,
        "project_id": "proj_prod_wind_energy_099"
    }
    response = client.post("/api/v1/carbon/offsets/purchase", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["amount_kg"] == 5.1
    assert data["price_usd"] == 0.15
    assert data["status"] == "completed"
    assert "https://certificates.patch.io" in data["certificate_url"]


def test_scenario_14_patch_api_failure_retry_queue(client):
    """
    Scenario 14: Handling of Patch API failure during checkout (Resilience)
    Given Patch API encounters an outage/error during checkout
    When the offset purchase request fails
    Then the order completes successfully and queues the purchase into dead-letter retry queue
    """
    OffsetService.RETRY_QUEUE.clear()
    payload = {
        "order_id": "ord_fail_retry_1",
        "customer_id": "cust_123",
        "total_carbon_kg": 4.5
    }
    # Pass simulate_failure query param
    response = client.post("/api/v1/carbon/offsets/purchase?simulate_failure=true", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "retry_queued"
    assert data["retry_queued"] is True
    assert len(OffsetService.RETRY_QUEUE) > 0
    assert OffsetService.RETRY_QUEUE[-1]["order_id"] == "ord_fail_retry_1"


def test_scenario_15_immutable_write_to_carbon_ledger(client):
    """
    Scenario 15: Immutable write to transactional carbon ledger (Data Integrity)
    Given a successful offset purchase completed for order "ord_999"
    When the transaction is written to transactional_carbon_ledger table
    Then record is marked is_offset = True and has a valid cryptographic block hash
    """
    payload = {
        "order_id": "ord_999",
        "customer_id": "cust_999",
        "total_product_co2e": 4.2,
        "total_shipping_co2e": 0.9,
        "is_offset": True,
        "offset_amount_usd": 0.15,
        "offset_provider_transaction_id": "off_tx_test_999",
        "offset_certificate_url": "https://certificates.patch.io/pdf/off_tx_test_999.pdf"
    }
    response = client.post("/api/v1/carbon/ledger", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == "ord_999"
    assert data["is_offset"] is True
    assert data["total_order_co2e"] == 5.1
    assert len(data["block_hash"]) == 64  # SHA-256


def test_scenario_16_verification_offset_amount_calculation():
    """
    Scenario 16: Verification of offset amount calculation (Validation)
    Given an order with total carbon footprint of 10.0 kg CO2e
    When offset cost is calculated at $30.00 per metric ton
    Then system calculates offset cost as exactly $0.30 USD
    """
    price = OffsetService.calculate_offset_price_usd(10.0)
    assert price == 0.30

    price_5_1 = OffsetService.calculate_offset_price_usd(5.1)
    assert price_5_1 == 0.15


def test_scenario_17_customer_opts_out_of_offsetting(client):
    """
    Scenario 17: Customer opts out of carbon offsetting (Positive)
    Given a customer completes an order with "Offset-at-Checkout" toggle disabled
    When transaction is recorded in ledger
    Then is_offset is FALSE and offset_amount is 0.00
    """
    payload = {
        "order_id": "ord_no_offset",
        "customer_id": "cust_no_offset",
        "total_product_co2e": 3.0,
        "total_shipping_co2e": 1.0,
        "is_offset": False,
        "offset_amount_usd": 0.0
    }
    response = client.post("/api/v1/carbon/ledger", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_offset"] is False
    assert data["offset_amount_usd"] == 0.0


def test_scenario_18_sql_injection_prevention(client, db_session):
    """
    Scenario 18: SQL Injection prevention on ledger queries (Security)
    Given a malicious user attempts to query the carbon ledger using SQL injection payloads
    When the request is processed by the Carbon Footprint Engine
    Then parameterized SQL queries safely handle the string without leaking or altering data
    """
    malicious_order_id = "ord_1' OR '1'='1"
    res = LedgerService.get_entry_by_order_id_safe(malicious_order_id, db_session)
    # Safely returns None because no record matches this literal order_id string
    assert res is None

    # Endpoint returns 404
    response = client.get(f"/api/v1/carbon/ledger/{malicious_order_id}")
    assert response.status_code == 404
