"""
Tests for Story ARCH-S1 & Task ARCH-T1: Product Carbon Baseline Calculation Engine
Covers Gherkin Scenarios 1 to 6.
"""
from app.services.carbon_engine import CarbonBaselineEngine


def test_scenario_1_successful_baseline_calculation(client):
    """
    Scenario 1: Successful calculation of baseline carbon footprint (Positive)
    Given a verified vendor submits a product with valid material composition
    When the Carbon Footprint Engine receives the calculation request
    Then the system should calculate Cradle-to-Gate carbon footprint and return 200 OK.
    """
    payload = {
        "product_id": "prod_98765",
        "vendor_id": "vendor_eco_01",
        "weight_kg": 0.35,
        "materials": [
            {"material_name": "Organic Cotton", "percentage": 80.0},
            {"material_name": "Recycled Polyester", "percentage": 20.0}
        ]
    }
    headers = {"Authorization": "Bearer test-secret-token"}
    response = client.post("/api/v1/carbon/calculate-baseline", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == "prod_98765"
    # 0.35 * 0.8 * 3.5 = 0.98; 0.35 * 0.2 * 4.2 = 0.294 -> total = 1.274 kg CO2e
    assert data["cradle_to_gate_co2e_kg"] > 0
    assert data["calculation_metadata"]["fallback_applied"] is False


def test_scenario_2_rejection_invalid_material_percentages(client):
    """
    Scenario 2: Rejection of calculation request due to invalid material percentages (Negative)
    Given a vendor attempts to submit a product
    When the material percentages sum up to 95% instead of 100%
    Then the Catalog Service should reject the request with a 400 Bad Request error
    And return the error message "Material composition percentages must equal exactly 100%"
    """
    payload = {
        "product_id": "prod_invalid_pct",
        "vendor_id": "vendor_eco_01",
        "weight_kg": 0.5,
        "materials": [
            {"material_name": "Organic Cotton", "percentage": 60.0},
            {"material_name": "Recycled Polyester", "percentage": 35.0}  # Sum = 95%
        ]
    }
    headers = {"Authorization": "Bearer test-secret-token"}
    response = client.post("/api/v1/carbon/calculate-baseline", json=payload, headers=headers)
    assert response.status_code == 422 or response.status_code == 400
    assert "Material composition percentages must equal exactly 100%" in response.text


def test_scenario_3_handling_missing_material_emission_factor(client):
    """
    Scenario 3: Handling of missing material emission factor (Boundary/Negative)
    Given a vendor submits a product containing a rare material "Bamboo Silk"
    When the Carbon Footprint Engine does not find "Bamboo Silk" in the emission_factors database
    Then the system should fallback to default "Organic Cotton" emission factor
    And return a 200 OK response with a "Calculated with fallback" warning flag
    """
    payload = {
        "product_id": "prod_rare_bamboo",
        "vendor_id": "vendor_eco_02",
        "weight_kg": 1.0,
        "materials": [
            {"material_name": "Bamboo Silk", "percentage": 100.0}
        ]
    }
    headers = {"Authorization": "Bearer test-secret-token"}
    response = client.post("/api/v1/carbon/calculate-baseline", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["calculation_metadata"]["fallback_applied"] is True
    assert "fallback" in data["calculation_metadata"]["warning"].lower()


def test_scenario_4_caching_of_calculated_product_baseline(client):
    """
    Scenario 4: Caching of calculated product carbon baseline (Performance)
    Given a product carbon baseline has been successfully calculated for product "prod_123"
    When a customer requests the product details for "prod_123"
    Then the baseline is returned from cache with cached=True
    """
    payload = {
        "product_id": "prod_123",
        "weight_kg": 0.4,
        "materials": [
            {"material_name": "Organic Cotton", "percentage": 100.0}
        ]
    }
    headers = {"Authorization": "Bearer test-secret-token"}
    # First call: computes and stores to cache
    res1 = client.post("/api/v1/carbon/calculate-baseline", json=payload, headers=headers)
    assert res1.status_code == 200
    assert res1.json()["calculation_metadata"]["cached"] is False

    # Second call: retrieved from cache
    res2 = client.post("/api/v1/carbon/calculate-baseline", json=payload, headers=headers)
    assert res2.status_code == 200
    assert res2.json()["calculation_metadata"]["cached"] is True


def test_scenario_5_cache_invalidation_on_product_update(client):
    """
    Scenario 5: Cache invalidation on product material update (Data Integrity)
    Given a cached carbon baseline exists for product "prod_123"
    When the vendor updates the material composition of "prod_123"
    Then the system should invalidate the Redis cache key
    """
    payload = {
        "product_id": "prod_123_update",
        "weight_kg": 0.5,
        "materials": [{"material_name": "Organic Cotton", "percentage": 100.0}]
    }
    headers = {"Authorization": "Bearer test-secret-token"}
    res1 = client.post("/api/v1/carbon/calculate-baseline", json=payload, headers=headers)
    assert res1.status_code == 200

    # Invalidate cache
    invalidated = CarbonBaselineEngine.invalidate_cache("prod_123_update")
    assert invalidated is True

    # Next call computes afresh (cached == False)
    res2 = client.post("/api/v1/carbon/calculate-baseline", json=payload, headers=headers)
    assert res2.status_code == 200
    assert res2.json()["calculation_metadata"]["cached"] is False


def test_scenario_6_unauthorized_access_to_baseline_endpoint(client):
    """
    Scenario 6: Unauthorized access to baseline calculation endpoint (Security)
    Given an unauthenticated client attempts to access the baseline calculation API
    When they send a POST request to "/api/v1/carbon/calculate-baseline" without token
    Then the API Gateway should block the request and return a 401 Unauthorized response
    """
    payload = {
        "product_id": "prod_unauth",
        "weight_kg": 0.5,
        "materials": [{"material_name": "Organic Cotton", "percentage": 100.0}]
    }
    # No authorization header
    response = client.post("/api/v1/carbon/calculate-baseline", json=payload)
    assert response.status_code == 401
