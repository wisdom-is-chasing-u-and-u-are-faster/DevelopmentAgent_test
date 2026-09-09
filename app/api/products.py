from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
import sqlite3
from app.db.session import get_db

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("")
def list_products(
    category: Optional[str] = None,
    undertone: Optional[str] = None,
    finish: Optional[str] = None,
    depth: Optional[str] = None,
    search: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    AC: A user can browse products, filter them by shade attributes, and view a product detail page.
    """
    query = "SELECT DISTINCT p.* FROM products p"
    joins = []
    conditions = []
    params = []

    if undertone or finish or depth:
        joins.append("JOIN product_shades s ON p.id = s.product_id")
        if undertone:
            conditions.append("LOWER(s.undertone) = LOWER(?)")
            params.append(undertone)
        if finish:
            conditions.append("LOWER(s.finish) = LOWER(?)")
            params.append(finish)
        if depth:
            conditions.append("LOWER(s.depth) = LOWER(?)")
            params.append(depth)

    if category:
        conditions.append("LOWER(p.category) = LOWER(?)")
        params.append(category)

    if search:
        conditions.append("(LOWER(p.name) LIKE LOWER(?) OR LOWER(p.brand) LIKE LOWER(?))")
        params.append(f"%{search}%")
        params.append(f"%{search}%")

    if joins:
        query += " " + " ".join(joins)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY p.id ASC"

    cursor = db.execute(query, params)
    products = [dict(row) for row in cursor.fetchall()]

    for p in products:
        shades_cursor = db.execute(
            "SELECT * FROM product_shades WHERE product_id = ? ORDER BY id ASC", (p["id"],)
        )
        p["shades"] = [dict(row) for row in shades_cursor.fetchall()]

    return {"products": products, "total": len(products)}


@router.get("/{product_id}")
def get_product(product_id: int, db: sqlite3.Connection = Depends(get_db)):
    """
    AC: A user can browse products, filter them by shade attributes, and view a product detail page.
    """
    cursor = db.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")

    product = dict(row)
    shades_cursor = db.execute(
        "SELECT * FROM product_shades WHERE product_id = ? ORDER BY id ASC", (product_id,)
    )
    product["shades"] = [dict(row) for row in shades_cursor.fetchall()]
    return product
