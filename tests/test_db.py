import pytest
from app.db.init_db import init_database
from app.db.session import get_db_connection


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    test_db_file = str(tmp_path / "test_cosmetics.db")
    monkeypatch.setenv("COSMETICS_DB_PATH", test_db_file)
    init_database(test_db_file)
    yield


def test_schema_and_seed_data_loaded():
    conn = get_db_connection()
    cursor = conn.execute("SELECT COUNT(*) as cnt FROM products")
    assert cursor.fetchone()["cnt"] >= 4

    shades_cursor = conn.execute("SELECT COUNT(*) as cnt FROM product_shades")
    assert shades_cursor.fetchone()["cnt"] >= 30

    users_cursor = conn.execute("SELECT COUNT(*) as cnt FROM users")
    assert users_cursor.fetchone()["cnt"] >= 2
    conn.close()
