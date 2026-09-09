from fastapi import APIRouter, Depends, HTTPException
import sqlite3
from app.db.session import get_db

router = APIRouter(prefix="/account", tags=["Account"])


@router.get("/dashboard")
def get_account_dashboard(user_id: int = 1, db: sqlite3.Connection = Depends(get_db)):
    """
    AC: A user can log in, view their account dashboard, and see their order history.
    """
    user_cursor = db.execute("SELECT id, email, full_name, created_at FROM users WHERE id = ?", (user_id,))
    user_row = user_cursor.fetchone()
    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")

    loyalty_cursor = db.execute(
        "SELECT tier, points_balance, lifetime_points FROM loyalty_accounts WHERE user_id = ?",
        (user_id,)
    )
    loyalty_row = loyalty_cursor.fetchone()

    orders_cursor = db.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (user_id,))
    orders = [dict(row) for row in orders_cursor.fetchall()]

    for o in orders:
        items_cursor = db.execute(
            """
            SELECT oi.*, p.name as product_name, s.shade_name, s.hex_code
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            LEFT JOIN product_shades s ON oi.shade_id = s.id
            WHERE oi.order_id = ?
            """,
            (o["id"],)
        )
        o["items"] = [dict(row) for row in items_cursor.fetchall()]

    return {
        "user": dict(user_row),
        "loyalty": (
            dict(loyalty_row) if loyalty_row else {"tier": "Bronze", "points_balance": 0, "lifetime_points": 0}
        ),
        "orders": orders
    }
