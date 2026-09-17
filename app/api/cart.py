from fastapi import APIRouter, Depends, HTTPException
import sqlite3
from app.db.session import get_db
from app.models.cosmetics import CartItemCreate

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("")
def get_cart(user_id: int = 1, db: sqlite3.Connection = Depends(get_db)):
    """
    AC: A user can add a product to the cart, proceed to checkout, and complete a mock purchase.
    """
    cursor = db.execute(
        """
        SELECT c.*, p.name as product_name, p.price as unit_price, p.image_url,
               s.shade_name, s.hex_code
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        LEFT JOIN product_shades s ON c.shade_id = s.id
        WHERE c.user_id = ?
        ORDER BY c.id ASC
        """,
        (user_id,)
    )
    items = [dict(row) for row in cursor.fetchall()]
    subtotal = sum(item["unit_price"] * item["quantity"] for item in items)
    total_items = sum(item["quantity"] for item in items)
    return {"items": items, "subtotal": round(subtotal, 2), "item_count": total_items}


@router.post("")
def add_to_cart(item: CartItemCreate, user_id: int = 1, db: sqlite3.Connection = Depends(get_db)):
    """
    AC: A user can add a product to the cart, proceed to checkout, and complete a mock purchase.
    """
    cursor = db.execute(
        """
        INSERT INTO cart_items (
            session_id, user_id, product_id, shade_id, quantity,
            is_subscription, subscription_frequency_weeks
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            f"sess_user_{user_id}",
            user_id,
            item.product_id,
            item.shade_id,
            item.quantity,
            1 if item.is_subscription else 0,
            item.subscription_frequency_weeks,
        )
    )
    db.commit()
    return {"status": "success", "cart_item_id": cursor.lastrowid}


@router.delete("/{item_id}")
def remove_from_cart(item_id: int, user_id: int = 1, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("DELETE FROM cart_items WHERE id = ? AND user_id = ?", (item_id, user_id))
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"status": "deleted"}
