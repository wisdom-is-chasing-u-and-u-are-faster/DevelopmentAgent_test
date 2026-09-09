import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    test_db_file = str(tmp_path / "test_cosmetics.db")
    monkeypatch.setenv("COSMETICS_DB_PATH", test_db_file)
    init_database(test_db_file)
    yield


client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_full_d2c_customer_journey():
    """
    E2E Journey:
    1. Take Shade Quiz -> Get Matched Shade
    2. Add Recommended Product/Shade to Cart
    3. Complete Tokenized Checkout
    4. View Account Dashboard Order History
    5. Manage Active Subscriptions (Skip & Swap)
    """
    # 1. Take Shade Quiz
    quiz_res = client.post(
        "/api/v1/shade-finder/match",
        json={"skin_tone": "Tan", "undertone": "Warm", "finish_preference": "Dewy"}
    )
    assert quiz_res.status_code == 200
    matched = quiz_res.json()
    prod_id = matched["recommended_product"]["id"]
    shade_id = matched["matched_shade_id"]

    # 2. Add to Cart as Subscription
    cart_res = client.post(
        "/api/v1/cart?user_id=2",
        json={
            "product_id": prod_id,
            "shade_id": shade_id,
            "quantity": 1,
            "is_subscription": True,
            "subscription_frequency_weeks": 6
        }
    )
    assert cart_res.status_code == 200

    # 3. Checkout
    checkout_res = client.post(
        "/api/v1/checkout",
        json={
            "payment_token": "tok_visa_mock_9999",
            "shipping_address": "456 Market St, San Francisco, CA",
            "user_id": 2
        }
    )
    assert checkout_res.status_code == 200
    order_data = checkout_res.json()
    assert order_data["status"] == "confirmed"

    # 4. View Dashboard
    dash_res = client.get("/api/v1/account/dashboard?user_id=2")
    assert dash_res.status_code == 200
    assert len(dash_res.json()["orders"]) >= 1

    # 5. Manage Subscriptions
    subs_res = client.get("/api/v1/subscriptions?user_id=2")
    assert subs_res.status_code == 200
    subs = subs_res.json()["subscriptions"]
    assert len(subs) >= 1
