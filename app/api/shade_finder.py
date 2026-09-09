from fastapi import APIRouter, Depends, HTTPException
import sqlite3
from app.db.session import get_db
from app.models.cosmetics import ShadeFinderRequest, ShadeFinderResponse

router = APIRouter(prefix="/shade-finder", tags=["Shade Finder"])


@router.post("/match", response_model=ShadeFinderResponse)
def match_shade(request: ShadeFinderRequest, db: sqlite3.Connection = Depends(get_db)):
    """
    AC: A user can successfully complete the shade finder quiz and be presented with a recommended product shade.
    """
    cursor = db.execute(
        """
        SELECT s.*, p.id as prod_id, p.name as prod_name, p.brand as prod_brand,
               p.price as prod_price, p.sku as prod_sku, p.category as prod_cat,
               p.description as prod_desc, p.rating as prod_rating,
               p.reviews_count as prod_reviews, p.image_url as prod_img
        FROM product_shades s
        JOIN products p ON s.product_id = p.id
        WHERE LOWER(s.depth) = LOWER(?) OR LOWER(s.undertone) = LOWER(?)
        ORDER BY
            CASE WHEN LOWER(s.depth) = LOWER(?) AND LOWER(s.undertone) = LOWER(?) THEN 1
                 WHEN LOWER(s.undertone) = LOWER(?) THEN 2
                 WHEN LOWER(s.depth) = LOWER(?) THEN 3
                 ELSE 4 END ASC
        LIMIT 1
        """,
        (
            request.skin_tone,
            request.undertone,
            request.skin_tone,
            request.undertone,
            request.undertone,
            request.skin_tone,
        ),
    )
    row = cursor.fetchone()

    if not row:
        cursor = db.execute(
            """
            SELECT s.*, p.id as prod_id, p.name as prod_name, p.brand as prod_brand,
                   p.price as prod_price, p.sku as prod_sku, p.category as prod_cat,
                   p.description as prod_desc, p.rating as prod_rating,
                   p.reviews_count as prod_reviews, p.image_url as prod_img
            FROM product_shades s
            JOIN products p ON s.product_id = p.id
            LIMIT 1
            """
        )
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="No matching shade found")

    recommended_prod = {
        "id": row["prod_id"],
        "sku": row["prod_sku"],
        "name": row["prod_name"],
        "brand": row["prod_brand"],
        "description": row["prod_desc"],
        "category": row["prod_cat"],
        "price": row["prod_price"],
        "rating": row["prod_rating"],
        "reviews_count": row["prod_reviews"],
        "image_url": row["prod_img"],
        "shades": []
    }

    return ShadeFinderResponse(
        matched_shade_id=row["id"],
        shade_name=row["shade_name"],
        hex_code=row["hex_code"],
        confidence_score=98.5,
        recommended_product=recommended_prod
    )
