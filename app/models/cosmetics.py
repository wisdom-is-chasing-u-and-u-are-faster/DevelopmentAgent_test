from typing import List, Optional
from pydantic import BaseModel, Field


class ShadeModel(BaseModel):
    id: int
    product_id: int
    shade_code: str
    shade_name: str
    hex_code: str
    undertone: str
    finish: str
    depth: str
    stock_quantity: int


class ProductModel(BaseModel):
    id: int
    sku: str
    name: str
    brand: str
    description: Optional[str] = None
    category: str
    price: float
    rating: float = 4.8
    reviews_count: int = 100
    image_url: Optional[str] = None
    shades: List[ShadeModel] = Field(default_factory=list)


class ShadeFinderRequest(BaseModel):
    skin_tone: str
    undertone: str
    finish_preference: Optional[str] = "Natural"
    coverage: Optional[str] = "Medium"


class ShadeFinderResponse(BaseModel):
    matched_shade_id: int
    shade_name: str
    hex_code: str
    confidence_score: float
    recommended_product: ProductModel


class CartItemCreate(BaseModel):
    product_id: int
    shade_id: Optional[int] = None
    quantity: int = 1
    is_subscription: bool = False
    subscription_frequency_weeks: Optional[int] = 4


class CheckoutRequest(BaseModel):
    payment_token: str
    shipping_address: str
    user_id: int = 1


class SubscriptionSwapRequest(BaseModel):
    new_shade_id: int
