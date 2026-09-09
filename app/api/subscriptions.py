from fastapi import APIRouter, Depends, HTTPException
import sqlite3
from app.db.session import get_db
from app.models.cosmetics import SubscriptionSwapRequest

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("")
def list_subscriptions(user_id: int = 1, db: sqlite3.Connection = Depends(get_db)):
    """
    AC: A user can view their active subscriptions and perform 'skip' or 'swap' actions.
    """
    cursor = db.execute(
        """
        SELECT sub.*, p.name as product_name, p.price as unit_price, p.image_url,
               s.shade_name, s.hex_code, s.shade_code
        FROM subscriptions sub
        JOIN products p ON sub.product_id = p.id
        JOIN product_shades s ON sub.shade_id = s.id
        WHERE sub.user_id = ?
        ORDER BY sub.id ASC
        """,
        (user_id,)
    )
    return {"subscriptions": [dict(row) for row in cursor.fetchall()]}


@router.post("/{sub_id}/skip")
def skip_subscription(sub_id: int, user_id: int = 1, db: sqlite3.Connection = Depends(get_db)):
    """
    AC: A user can view their active subscriptions and perform 'skip' or 'swap' actions.
    """
    cursor = db.execute(
        "UPDATE subscriptions SET status = 'skipped', next_delivery_date = '2026-11-01' WHERE id = ? AND user_id = ?",
        (sub_id, user_id)
    )
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"status": "skipped", "next_delivery_date": "2026-11-01"}


@router.post("/{sub_id}/swap")
def swap_subscription_shade(
    sub_id: int, request: SubscriptionSwapRequest, user_id: int = 1, db: sqlite3.Connection = Depends(get_db)
):
    """
    AC: A user can view their active subscriptions and perform 'skip' or 'swap' actions.
    """
    shade_cursor = db.execute("SELECT shade_name FROM product_shades WHERE id = ?", (request.new_shade_id,))
    shade_row = shade_cursor.fetchone()
    if not shade_row:
        raise HTTPException(status_code=400, detail="Invalid shade ID")

    cursor = db.execute(
        "UPDATE subscriptions SET shade_id = ? WHERE id = ? AND user_id = ?",
        (request.new_shade_id, sub_id, user_id)
    )
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"status": "swapped", "new_shade_id": request.new_shade_id, "new_shade_name": shade_row["shade_name"]}
