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


def test_cart_operations():
    """AC: A user can add a product to the cart, proceed to checkout, and complete a mock purchase."""
    # Get current cart
    get_res = client.get("/api/v1/cart?user_id=1")
    assert get_res.status_code == 200
    initial_count = get_res.json()["item_count"]

    # Add item to cart
    add_payload = {
        "product_id": 1,
        "shade_id": 5,
        "quantity": 2,
        "is_subscription": False
    }
    add_res = client.post("/api/v1/cart?user_id=1", json=add_payload)
    assert add_res.status_code == 200
    item_id = add_res.json()["cart_item_id"]

    # Verify updated cart
    get_res2 = client.get("/api/v1/cart?user_id=1")
    assert get_res2.json()["item_count"] == initial_count + 2

    # Remove item
    del_res = client.delete(f"/api/v1/cart/{item_id}?user_id=1")
    assert del_res.status_code == 200


def test_checkout_and_order_creation():
    """AC: A user can add a product to the cart, proceed to checkout, and complete a mock purchase."""
    checkout_payload = {
        "payment_token": "tok_mock_amex_8888",
        "shipping_address": "100 Broadway, New York, NY 10005",
        "user_id": 1
    }
    res = client.post("/api/v1/checkout", json=checkout_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "confirmed"
    assert data["order_id"] > 0
    assert data["total_amount"] > 0
    assert data["points_earned"] > 0

    # Verify cart is empty after checkout
    cart_res = client.get("/api/v1/cart?user_id=1")
    assert cart_res.json()["item_count"] == 0


def test_account_dashboard():
    """AC: A user can log in, view their account dashboard, and see their order history."""
    res = client.get("/api/v1/account/dashboard?user_id=1")
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["email"] == "elena.rostova@example.com"
    assert "tier" in data["loyalty"]
    assert len(data["orders"]) >= 1


def test_subscriptions_skip_and_swap():
    """AC: A user can view their active subscriptions and perform 'skip' or 'swap' actions."""
    # List subscriptions
    list_res = client.get("/api/v1/subscriptions?user_id=1")
    assert list_res.status_code == 200
    subs = list_res.json()["subscriptions"]
    assert len(subs) >= 1
    sub_id = subs[0]["id"]

    # Skip subscription
    skip_res = client.post(f"/api/v1/subscriptions/{sub_id}/skip?user_id=1")
    assert skip_res.status_code == 200
    assert skip_res.json()["status"] == "skipped"

    # Swap subscription shade
    swap_res = client.post(
        f"/api/v1/subscriptions/{sub_id}/swap?user_id=1",
        json={"new_shade_id": 10}
    )
    assert swap_res.status_code == 200
    assert swap_res.json()["status"] == "swapped"
    assert swap_res.json()["new_shade_name"] == "Golden Sand"
