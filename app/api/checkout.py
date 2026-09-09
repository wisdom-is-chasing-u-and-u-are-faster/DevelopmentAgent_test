import uuid
from fastapi import APIRouter, Depends, HTTPException
import sqlite3
from app.db.session import get_db
from app.models.cosmetics import CheckoutRequest

router = APIRouter(prefix="/checkout", tags=["Checkout"])


@router.post("")
def process_checkout(request: CheckoutRequest, db: sqlite3.Connection = Depends(get_db)):
    """
    AC: A user can add a product to the cart, proceed to checkout, and complete a mock purchase.
    """
    cursor = db.execute(
        """
        SELECT c.*, p.price as unit_price
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
        """,
        (request.user_id,)
    )
    cart_items = [dict(row) for row in cursor.fetchall()]

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cannot checkout with empty cart")

    total_amount = sum(item["unit_price"] * item["quantity"] for item in cart_items)
    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    cursor = db.execute(
        """
        INSERT INTO orders (order_number, user_id, status, total_amount, payment_token, shipping_address)
        VALUES (?, ?, 'confirmed', ?, ?, ?)
        """,
        (order_number, request.user_id, round(total_amount, 2), request.payment_token, request.shipping_address)
    )
    order_id = cursor.lastrowid

    for item in cart_items:
        db.execute(
            """
            INSERT INTO order_items (order_id, product_id, shade_id, quantity, unit_price)
            VALUES (?, ?, ?, ?, ?)
            """,
            (order_id, item["product_id"], item["shade_id"], item["quantity"], item["unit_price"])
        )
        if item["is_subscription"]:
            db.execute(
                """
                INSERT INTO subscriptions (user_id, product_id, shade_id, frequency_weeks, status, next_delivery_date)
                VALUES (?, ?, ?, ?, 'active', '2026-10-15')
                """,
                (request.user_id, item["product_id"], item["shade_id"], item["subscription_frequency_weeks"] or 4)
            )

    # Award loyalty points (10 points per dollar spent)
    points_earned = int(total_amount * 10)
    db.execute(
        """
        UPDATE loyalty_accounts
        SET points_balance = points_balance + ?, lifetime_points = lifetime_points + ?
        WHERE user_id = ?
        """,
        (points_earned, points_earned, request.user_id)
    )

    # Clear Cart
    db.execute("DELETE FROM cart_items WHERE user_id = ?", (request.user_id,))
    db.commit()

    return {
        "order_id": order_id,
        "order_number": order_number,
        "status": "confirmed",
        "total_amount": round(total_amount, 2),
        "points_earned": points_earned
    }
