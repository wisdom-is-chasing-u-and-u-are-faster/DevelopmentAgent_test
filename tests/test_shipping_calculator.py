"""
Tests for Story ARCH-S2: Dynamic Shipping Carbon Calculation
Covers Gherkin Scenarios 7 to 12.
"""
from fastapi import HTTPException
from app.api.v1.endpoints.carbon import rate_limit_check, RATE_LIMIT_STORE


def test_scenario_7_successful_shipping_carbon_calculation(client):
    """
    Scenario 7: Successful calculation of shipping carbon footprint (Positive)
    Given a customer proceeds to checkout with a valid shipping address (90210 to 10001, 1.2kg)
    When the Carbon Footprint Engine receives the origin, destination, and package weight
    Then the system should calculate shipping distance (3940.5 km) and return 0.85 kg CO2e
    """
    payload = {
        "origin_zip": "90210",
        "destination_zip": "10001",
        "weight_kg": 1.2,
        "carrier": "UPS"
    }
    response = client.post("/api/v1/carbon/calculate-shipping", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["distance_km"] == 3940.5
    assert data["shipping_co2e_kg"] == 0.85


def test_scenario_8_rejection_invalid_zip_code(client):
    """
    Scenario 8: Rejection of shipping calculation due to invalid zip code (Negative)
    Given a customer enters an invalid shipping zip code "00000"
    When the checkout system requests the shipping carbon calculation
    Then the Carbon Footprint Engine should return a 400 Bad Request error
    And return the error message "Invalid origin or destination zip code"
    """
    payload = {
        "origin_zip": "00000",
        "destination_zip": "10001",
        "weight_kg": 1.0,
        "carrier": "UPS"
    }
    response = client.post("/api/v1/carbon/calculate-shipping", json=payload)
    assert response.status_code == 400
    assert "Invalid origin or destination zip code" in response.text


def test_scenario_9_handling_international_shipping(client):
    """
    Scenario 9: Handling of international shipping calculations (Boundary)
    Given a customer enters an international shipping destination in Spain (ES, 28001)
    When the checkout system requests shipping carbon calculation
    Then the system applies international logistics factors and returns calculated CO2e
    """
    payload = {
        "origin_zip": "10001",
        "destination_zip": "28001",
        "weight_kg": 2.0,
        "carrier": "AIR_FREIGHT"
    }
    response = client.post("/api/v1/carbon/calculate-shipping", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["shipping_co2e_kg"] > 0
    assert data["distance_km"] > 0


def test_scenario_10_rate_limiting_shipping_endpoint():
    """
    Scenario 10: Rate limiting on shipping calculation endpoint (Security)
    Given a client sends more than 100 requests per minute to the shipping calculation API
    When the rate limit threshold is exceeded
    Then the API Gateway should block subsequent requests and return a 429 Too Many Requests error
    """
    test_ip = "192.168.1.55"
    RATE_LIMIT_STORE.pop(test_ip, None)

    # Make 100 successful rate-limit checks
    for _ in range(100):
        rate_limit_check(client_ip=test_ip, limit=100)

    # 101st request must trigger 429
    try:
        rate_limit_check(client_ip=test_ip, limit=100)
        assert False, "Expected 429 Too Many Requests exception"
    except HTTPException as e:
        assert e.status_code == 429
        assert "Rate limit exceeded" in e.detail


def test_scenario_11_fallback_mechanism_when_logistics_offline(client):
    """
    Scenario 11: Fallback mechanism when logistics API is offline (Resilience)
    Given an unknown zip code routing without live geocoding
    When shipping carbon calculation is requested
    Then the system falls back to static distance-matrix calculation and returns 200 OK
    """
    payload = {
        "origin_zip": "99999",
        "destination_zip": "88888",
        "weight_kg": 1.5,
        "carrier": "UPS"
    }
    response = client.post("/api/v1/carbon/calculate-shipping", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["fallback_applied"] is True
    assert data["shipping_co2e_kg"] > 0


def test_scenario_12_zero_weight_shipping_validation(client):
    """
    Scenario 12: Zero weight shipping calculation validation (Boundary)
    Given a customer attempts to checkout with total weight "0.0kg"
    When shipping carbon calculation is triggered
    Then the system rejects with a 400 Bad Request error
    And returns "Package weight must be greater than zero"
    """
    payload = {
        "origin_zip": "90210",
        "destination_zip": "10001",
        "weight_kg": 0.0,
        "carrier": "UPS"
    }
    response = client.post("/api/v1/carbon/calculate-shipping", json=payload)
    assert response.status_code == 400
    assert "Package weight must be greater than zero" in response.text
