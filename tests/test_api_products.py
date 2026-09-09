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


def test_list_products_all():
    """AC: A user can browse products, filter them by shade attributes, and view a product detail page."""
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 4
    assert len(data["products"]) >= 4
    assert len(data["products"][0]["shades"]) > 0


def test_filter_products_by_undertone_and_depth():
    """AC: A user can browse products, filter them by shade attributes, and view a product detail page."""
    response = client.get("/api/v1/products?undertone=Warm&depth=Medium")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


def test_get_single_product_detail():
    """AC: A user can browse products, filter them by shade attributes, and view a product detail page."""
    response = client.get("/api/v1/products/1")
    assert response.status_code == 200
    product = response.json()
    assert product["id"] == 1
    assert "Luminous Silk" in product["name"]
    assert len(product["shades"]) >= 20


def test_get_nonexistent_product():
    response = client.get("/api/v1/products/99999")
    assert response.status_code == 404
